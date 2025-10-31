-- ============================================================================
-- Clinic Cancellation Chatbot - Database Schema
-- ============================================================================
-- Description: Complete PostgreSQL schema for SMS-based cancellation management
-- Version: 0.1.0
-- Author: Jonathan Ives (@dollythedog)
-- Last Updated: 2025-10-31
-- ============================================================================

-- Drop existing types and tables (for clean reinstall)
DROP TABLE IF EXISTS message_log CASCADE;
DROP TABLE IF EXISTS offer CASCADE;
DROP TABLE IF EXISTS cancellation_event CASCADE;
DROP TABLE IF EXISTS waitlist_entry CASCADE;
DROP TABLE IF EXISTS provider_reference CASCADE;
DROP TABLE IF EXISTS patient_contact CASCADE;
DROP TABLE IF EXISTS staff_user CASCADE;

DROP TYPE IF EXISTS message_status CASCADE;
DROP TYPE IF EXISTS message_direction CASCADE;
DROP TYPE IF EXISTS offer_state CASCADE;
DROP TYPE IF EXISTS cancellation_status CASCADE;

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE cancellation_status AS ENUM (
    'open',           -- Slot available, offers being sent
    'filled',         -- Slot claimed by patient
    'expired',        -- No responses, slot expired
    'aborted'         -- Manually canceled by staff
);

CREATE TYPE offer_state AS ENUM (
    'pending',        -- Offer sent, awaiting response
    'accepted',       -- Patient accepted offer
    'declined',       -- Patient declined offer
    'expired',        -- Hold timer expired without response
    'canceled',       -- Offer canceled (slot filled by another)
    'failed'          -- SMS delivery failed
);

CREATE TYPE message_direction AS ENUM (
    'outbound',       -- SMS sent to patient
    'inbound'         -- SMS received from patient
);

CREATE TYPE message_status AS ENUM (
    'queued',         -- Twilio: message queued
    'sent',           -- Twilio: message sent to carrier
    'delivered',      -- Twilio: message delivered to device
    'undelivered',    -- Twilio: message failed to deliver
    'failed',         -- Twilio: message send failed
    'received'        -- Our system: inbound message received
);

-- ============================================================================
-- TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- patient_contact
-- ----------------------------------------------------------------------------
-- Stores minimal patient contact information for SMS communication
-- HIPAA Note: Store only essential data, no diagnoses or full medical records
-- ----------------------------------------------------------------------------
CREATE TABLE patient_contact (
    id SERIAL PRIMARY KEY,
    phone_e164 TEXT NOT NULL UNIQUE,                      -- E.164 format: +12145551234
    display_name TEXT,                                     -- First name or initials only
    last_contacted_at TIMESTAMP WITH TIME ZONE,           -- Last SMS sent timestamp
    opt_out BOOLEAN DEFAULT FALSE,                        -- STOP keyword received
    consent_source TEXT,                                  -- 'verbal', 'paper', 'sms', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_patient_phone ON patient_contact(phone_e164);
CREATE INDEX idx_patient_opt_out ON patient_contact(opt_out) WHERE opt_out = FALSE;

COMMENT ON TABLE patient_contact IS 'Minimal patient contact information for SMS communication';
COMMENT ON COLUMN patient_contact.phone_e164 IS 'Phone number in E.164 format (+12145551234)';
COMMENT ON COLUMN patient_contact.opt_out IS 'TRUE if patient sent STOP keyword';

-- ----------------------------------------------------------------------------
-- provider_reference
-- ----------------------------------------------------------------------------
-- Provider information for matching appointments to waitlist preferences
-- Can link to existing TPCCC provider database via external_provider_id
-- ----------------------------------------------------------------------------
CREATE TABLE provider_reference (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL,                          -- Full name (e.g., "Dr. Smith")
    provider_type TEXT NOT NULL,                          -- 'MD/DO', 'APP', 'NP', 'PA', etc.
    active BOOLEAN DEFAULT TRUE,                          -- Currently seeing patients
    external_provider_id TEXT,                            -- Link to existing provider DB
    tags TEXT[],                                          -- Optional: ['Clinic', 'Tele', etc.]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_provider_active ON provider_reference(active) WHERE active = TRUE;
CREATE INDEX idx_provider_type ON provider_reference(provider_type);

COMMENT ON TABLE provider_reference IS 'Provider information for appointment matching';
COMMENT ON COLUMN provider_reference.external_provider_id IS 'Foreign key to existing provider database';

-- ----------------------------------------------------------------------------
-- waitlist_entry
-- ----------------------------------------------------------------------------
-- Active waitlist entries with priority scoring and provider preferences
-- ----------------------------------------------------------------------------
CREATE TABLE waitlist_entry (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patient_contact(id) ON DELETE CASCADE,
    provider_preference TEXT[],                           -- Preferred provider names
    provider_type_preference TEXT,                        -- 'MD/DO', 'APP', 'Any'
    current_appt_at TIMESTAMP WITH TIME ZONE,            -- Next scheduled appointment
    urgent_flag BOOLEAN DEFAULT FALSE,                    -- High priority (+30 points)
    manual_boost INTEGER DEFAULT 0 CHECK (manual_boost BETWEEN 0 AND 40), -- Staff override
    active BOOLEAN DEFAULT TRUE,                          -- Currently on waitlist
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),     -- Waitlist enrollment date
    priority_score INTEGER,                               -- Calculated score (updated regularly)
    notes TEXT,                                           -- Staff notes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_waitlist_patient ON waitlist_entry(patient_id);
CREATE INDEX idx_waitlist_active ON waitlist_entry(active, urgent_flag) WHERE active = TRUE;
CREATE INDEX idx_waitlist_priority ON waitlist_entry(priority_score DESC NULLS LAST) WHERE active = TRUE;

COMMENT ON TABLE waitlist_entry IS 'Active waitlist with priority scoring';
COMMENT ON COLUMN waitlist_entry.manual_boost IS 'Admin-controlled priority boost (0-40 points)';
COMMENT ON COLUMN waitlist_entry.priority_score IS 'Calculated priority score (higher = more urgent)';

-- ----------------------------------------------------------------------------
-- cancellation_event
-- ----------------------------------------------------------------------------
-- Tracks canceled appointment slots and their fill status
-- ----------------------------------------------------------------------------
CREATE TABLE cancellation_event (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES provider_reference(id) ON DELETE SET NULL,
    location TEXT NOT NULL,                               -- Clinic location
    slot_start_at TIMESTAMP WITH TIME ZONE NOT NULL,      -- Appointment start time
    slot_end_at TIMESTAMP WITH TIME ZONE NOT NULL,        -- Appointment end time
    reason TEXT,                                          -- Optional cancellation reason
    status cancellation_status DEFAULT 'open',            -- Current status
    notes TEXT,                                           -- Staff notes or special instructions
    created_by_staff_id INTEGER,                          -- Staff member who logged it
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    filled_at TIMESTAMP WITH TIME ZONE,                   -- When slot was filled
    filled_by_patient_id INTEGER REFERENCES patient_contact(id) ON DELETE SET NULL,
    
    CONSTRAINT valid_slot_times CHECK (slot_end_at > slot_start_at)
);

CREATE INDEX idx_cancellation_status ON cancellation_event(status);
CREATE INDEX idx_cancellation_slot_start ON cancellation_event(slot_start_at);
CREATE INDEX idx_cancellation_provider ON cancellation_event(provider_id);

COMMENT ON TABLE cancellation_event IS 'Canceled appointment slots and fill status';
COMMENT ON COLUMN cancellation_event.filled_by_patient_id IS 'Patient who claimed the slot';

-- ----------------------------------------------------------------------------
-- offer
-- ----------------------------------------------------------------------------
-- Individual SMS offers sent to waitlist patients
-- Tracks batch number, hold timers, and response status
-- ----------------------------------------------------------------------------
CREATE TABLE offer (
    id SERIAL PRIMARY KEY,
    cancellation_id INTEGER NOT NULL REFERENCES cancellation_event(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patient_contact(id) ON DELETE CASCADE,
    batch_number INTEGER NOT NULL,                        -- Batch sequence (1, 2, 3, ...)
    offer_sent_at TIMESTAMP WITH TIME ZONE,              -- When SMS was sent
    hold_expires_at TIMESTAMP WITH TIME ZONE,            -- Hold window expiration
    state offer_state DEFAULT 'pending',                  -- Current offer state
    lock_token UUID DEFAULT gen_random_uuid(),           -- Unique token for race safety
    accepted_at TIMESTAMP WITH TIME ZONE,                -- When patient accepted
    declined_at TIMESTAMP WITH TIME ZONE,                -- When patient declined
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_offer_cancellation ON offer(cancellation_id);
CREATE INDEX idx_offer_patient ON offer(patient_id);
CREATE INDEX idx_offer_state ON offer(state);
CREATE INDEX idx_offer_hold_expires ON offer(hold_expires_at) WHERE state = 'pending';
CREATE UNIQUE INDEX idx_offer_lock_token ON offer(lock_token);

COMMENT ON TABLE offer IS 'Individual SMS offers with hold timers';
COMMENT ON COLUMN offer.batch_number IS 'Batch sequence number (3 offers per batch)';
COMMENT ON COLUMN offer.lock_token IS 'UUID for race-safe confirmation';
COMMENT ON COLUMN offer.hold_expires_at IS 'Offer expires after this time if no response';

-- ----------------------------------------------------------------------------
-- message_log
-- ----------------------------------------------------------------------------
-- Complete audit trail of all SMS messages (inbound and outbound)
-- Stores Twilio delivery status and raw webhook payloads
-- ----------------------------------------------------------------------------
CREATE TABLE message_log (
    id SERIAL PRIMARY KEY,
    offer_id INTEGER REFERENCES offer(id) ON DELETE SET NULL,  -- Null for STOP/HELP messages
    direction message_direction NOT NULL,                 -- inbound or outbound
    from_phone TEXT NOT NULL,                             -- Sender phone (E.164)
    to_phone TEXT NOT NULL,                               -- Recipient phone (E.164)
    body TEXT NOT NULL,                                   -- Message content (avoid PHI)
    twilio_sid TEXT,                                      -- Twilio message SID
    status message_status,                                -- Delivery status
    error_code INTEGER,                                   -- Twilio error code (if failed)
    error_message TEXT,                                   -- Twilio error message
    received_at TIMESTAMP WITH TIME ZONE,                -- When received (inbound)
    sent_at TIMESTAMP WITH TIME ZONE,                    -- When sent (outbound)
    delivered_at TIMESTAMP WITH TIME ZONE,               -- When delivered (status callback)
    raw_meta JSONB,                                       -- Full webhook payload for debugging
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_message_twilio_sid ON message_log(twilio_sid);
CREATE INDEX idx_message_offer ON message_log(offer_id);
CREATE INDEX idx_message_direction ON message_log(direction);
CREATE INDEX idx_message_created_at ON message_log(created_at DESC);
CREATE INDEX idx_message_from_phone ON message_log(from_phone);
CREATE INDEX idx_message_to_phone ON message_log(to_phone);

COMMENT ON TABLE message_log IS 'Complete audit trail of all SMS messages';
COMMENT ON COLUMN message_log.raw_meta IS 'Full Twilio webhook payload (JSONB)';
COMMENT ON COLUMN message_log.body IS 'Message text (avoid including PHI)';

-- ----------------------------------------------------------------------------
-- staff_user (optional for future admin authentication)
-- ----------------------------------------------------------------------------
CREATE TABLE staff_user (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'staff',                   -- 'admin', 'staff', 'readonly'
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_staff_email ON staff_user(email);
CREATE INDEX idx_staff_active ON staff_user(active) WHERE active = TRUE;

COMMENT ON TABLE staff_user IS 'Staff users for admin dashboard access';

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Auto-update updated_at timestamp
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_patient_contact_updated_at BEFORE UPDATE ON patient_contact
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_provider_reference_updated_at BEFORE UPDATE ON provider_reference
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_waitlist_entry_updated_at BEFORE UPDATE ON waitlist_entry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cancellation_event_updated_at BEFORE UPDATE ON cancellation_event
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_offer_updated_at BEFORE UPDATE ON offer
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staff_user_updated_at BEFORE UPDATE ON staff_user
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA (optional seed data)
-- ============================================================================

-- Sample providers (comment out if syncing from external database)
INSERT INTO provider_reference (provider_name, provider_type, active) VALUES
    ('Dr. Smith', 'MD/DO', TRUE),
    ('Dr. Johnson', 'MD/DO', TRUE),
    ('Sarah Williams, NP', 'APP', TRUE),
    ('Michael Brown, PA', 'APP', TRUE);

-- Sample staff user
INSERT INTO staff_user (email, role) VALUES
    ('admin@tpccc.com', 'admin');

-- ============================================================================
-- GRANTS (adjust based on your security model)
-- ============================================================================

-- Create read-only role for dashboard
-- CREATE ROLE chatbot_readonly;
-- GRANT CONNECT ON DATABASE clinic_chatbot TO chatbot_readonly;
-- GRANT USAGE ON SCHEMA public TO chatbot_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO chatbot_readonly;

-- Create read-write role for application
-- CREATE ROLE chatbot_app;
-- GRANT CONNECT ON DATABASE clinic_chatbot TO chatbot_app;
-- GRANT USAGE ON SCHEMA public TO chatbot_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO chatbot_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO chatbot_app;

-- ============================================================================
-- MAINTENANCE QUERIES (for reference)
-- ============================================================================

-- Calculate priority scores for all active waitlist entries
-- UPDATE waitlist_entry SET priority_score = (
--     CASE WHEN urgent_flag THEN 30 ELSE 0 END
--     + manual_boost
--     + CASE 
--         WHEN current_appt_at IS NULL THEN 0
--         WHEN current_appt_at - NOW() >= INTERVAL '180 days' THEN 20
--         WHEN current_appt_at - NOW() >= INTERVAL '90 days' THEN 10
--         WHEN current_appt_at - NOW() >= INTERVAL '30 days' THEN 5
--         ELSE 0
--       END
--     + LEAST(EXTRACT(EPOCH FROM (NOW() - joined_at)) / 86400 / 30, 10)::INTEGER
-- ) WHERE active = TRUE;

-- Archive old message logs (rotate after 90 days, keep metadata)
-- UPDATE message_log SET body = '[ARCHIVED]' 
-- WHERE created_at < NOW() - INTERVAL '90 days' AND body != '[ARCHIVED]';

-- Deactivate expired waitlist entries
-- UPDATE waitlist_entry SET active = FALSE
-- WHERE active = TRUE AND created_at < NOW() - INTERVAL '180 days';

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================
COMMENT ON DATABASE postgres IS 'Clinic Cancellation Chatbot v0.1.0 - 2025-10-31';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
