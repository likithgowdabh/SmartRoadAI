-- ==========================================================
-- SMARTROAD AI — DATABASE SCHEMA & ROW-LEVEL SECURITY (RLS)
-- Supports Supabase PostgreSQL and SQLite fallback
-- ==========================================================

-- 1. USERS & PROFILES TABLE
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('citizen', 'inspector', 'maintenance_manager', 'admin')),
    department TEXT DEFAULT 'Public Infrastructure',
    phone TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ROAD REPORTS TABLE
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    road_name TEXT NOT NULL,
    area TEXT NOT NULL,
    city TEXT NOT NULL DEFAULT 'Metropolis',
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('Critical', 'Medium', 'Low')),
    priority_score REAL NOT NULL DEFAULT 50.0,
    traffic_level TEXT NOT NULL DEFAULT 'Medium' CHECK (traffic_level IN ('Severe', 'High', 'Medium', 'Low')),
    repeat_count INTEGER NOT NULL DEFAULT 1,
    safety_risk TEXT NOT NULL DEFAULT 'Medium' CHECK (safety_risk IN ('High', 'Medium', 'Low')),
    status TEXT NOT NULL DEFAULT 'Reported' CHECK (status IN ('Reported', 'Under Inspection', 'Scheduled', 'In Progress', 'Repaired', 'Verified')),
    image_url TEXT,
    annotated_image_url TEXT,
    detection_count INTEGER NOT NULL DEFAULT 0,
    citizen_id TEXT,
    assigned_to TEXT,
    inspector_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (citizen_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 3. AI DETECTIONS TABLE
CREATE TABLE IF NOT EXISTS detections (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL,
    box_x1 INTEGER NOT NULL,
    box_y1 INTEGER NOT NULL,
    box_x2 INTEGER NOT NULL,
    box_y2 INTEGER NOT NULL,
    confidence REAL NOT NULL,
    class_name TEXT NOT NULL DEFAULT 'pothole',
    severity_rating TEXT DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 4. MAINTENANCE TASKS & WORK ORDERS
CREATE TABLE IF NOT EXISTS maintenance_tasks (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL,
    assigned_team TEXT NOT NULL,
    scheduled_date TEXT,
    due_date TEXT,
    completed_date TEXT,
    status TEXT NOT NULL DEFAULT 'Scheduled' CHECK (status IN ('Under Inspection', 'Scheduled', 'In Progress', 'Repaired', 'Verified')),
    repair_notes TEXT,
    before_image_url TEXT,
    after_image_url TEXT,
    budget_estimate REAL DEFAULT 0.0,
    cost_actual REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 5. AUDIT LOGS (Immutable tracking for municipal governance)
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info' CHECK (type IN ('info', 'warning', 'critical', 'success')),
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. SYSTEM SETTINGS
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================
-- SUPABASE POSTGRESQL ROW-LEVEL SECURITY (RLS) POLICIES
-- Note: SQLite safely ignores these statements
-- ==========================================================

-- Enable RLS on core tables
-- ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE maintenance_tasks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 1. Reports policy: Citizens can read all, create their own
-- CREATE POLICY "Public read access for reports" ON reports FOR SELECT USING (true);
-- CREATE POLICY "Citizen insert access" ON reports FOR INSERT WITH CHECK (auth.uid() = citizen_id OR citizen_id IS NULL);
-- CREATE POLICY "Inspector update access" ON reports FOR UPDATE USING (auth.jwt() ->> 'role' IN ('inspector', 'maintenance_manager', 'admin'));

-- 2. Maintenance tasks policy: Municipal staff only
-- CREATE POLICY "Staff maintenance access" ON maintenance_tasks FOR ALL USING (auth.jwt() ->> 'role' IN ('inspector', 'maintenance_manager', 'admin'));

-- 3. Audit logs policy: Append only, admin readable
-- CREATE POLICY "Audit append access" ON audit_logs FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Admin audit read access" ON audit_logs FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');
