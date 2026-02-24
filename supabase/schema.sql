-- LifeIO Supabase Schema

-- 1. Categories Table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    xp_multiplier DECIMAL(3, 2) NOT NULL DEFAULT 1.0,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- 2. Activities Table (Event-level storage)
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (end_time - start_time)) / 60
    ) STORED,
    xp_earned DECIMAL(10, 2), -- Calculated in backend or via trigger
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_time_range CHECK (end_time IS NULL OR end_time > start_time)
);

-- 3. Sleep Logs Table
CREATE TABLE sleep_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    sleep_time TIMESTAMP WITH TIME ZONE NOT NULL,
    wake_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (wake_time - sleep_time)) / 60
    ) STORED,
    quality INTEGER CHECK (quality >= 1 AND quality <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_sleep_range CHECK (wake_time > sleep_time)
);

-- 4. Daily Finance Table
CREATE TABLE daily_finance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    income DECIMAL(12, 2) DEFAULT 0,
    expense DECIMAL(12, 2) DEFAULT 0,
    net DECIMAL(12, 2) GENERATED ALWAYS AS (income - expense) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Enable RLS on all tables
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE sleep_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_finance ENABLE ROW LEVEL SECURITY;

-- RLS Policies (User can only access their own data)
CREATE POLICY "Users can manage their own categories" ON categories
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own activities" ON activities
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own sleep logs" ON sleep_logs
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own daily finance" ON daily_finance
    FOR ALL USING (auth.uid() = user_id);

-- Initial default categories for new users (Trigger function)
CREATE OR REPLACE FUNCTION public.handle_new_user_categories()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.categories (user_id, name, xp_multiplier, is_default)
    VALUES 
        (NEW.id, 'Work', 1.2, TRUE),
        (NEW.id, 'Study', 1.1, TRUE),
        (NEW.id, 'Workout', 1.3, TRUE),
        (NEW.id, 'Cooking', 1.0, TRUE),
        (NEW.id, 'Wasted Time', -1.0, TRUE);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create default categories on user signup
-- Note: This requires auth.users trigger setup in Supabase dashboard or SQL
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user_categories();
