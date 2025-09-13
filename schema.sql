-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar VARCHAR(500),
    username VARCHAR(50),
    provider VARCHAR(20),
    provider_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create learning preferences table
CREATE TABLE IF NOT EXISTS learning_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    visual_preference FLOAT DEFAULT 0.5 CHECK (visual_preference >= 0 AND visual_preference <= 1),
    auditory_preference FLOAT DEFAULT 0.5 CHECK (auditory_preference >= 0 AND auditory_preference <= 1),
    kinesthetic_preference FLOAT DEFAULT 0.5 CHECK (kinesthetic_preference >= 0 AND kinesthetic_preference <= 1),
    reading_preference FLOAT DEFAULT 0.5 CHECK (reading_preference >= 0 AND reading_preference <= 1),
    video_preference FLOAT DEFAULT 0.5 CHECK (video_preference >= 0 AND video_preference <= 1),
    article_preference FLOAT DEFAULT 0.5 CHECK (article_preference >= 0 AND article_preference <= 1),
    interactive_preference FLOAT DEFAULT 0.5 CHECK (interactive_preference >= 0 AND interactive_preference <= 1),
    course_preference FLOAT DEFAULT 0.5 CHECK (course_preference >= 0 AND course_preference <= 1),
    preferred_difficulty VARCHAR(20) DEFAULT 'intermediate' CHECK (preferred_difficulty IN ('beginner', 'intermediate', 'advanced')),
    preferred_session_length INTEGER DEFAULT 30 CHECK (preferred_session_length > 0),
    interests TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create content sources table
CREATE TABLE IF NOT EXISTS content_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url VARCHAR(500) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('video', 'article', 'course', 'interactive', 'podcast', 'book')),
    source_platform VARCHAR(100) NOT NULL,
    duration_minutes INTEGER CHECK (duration_minutes > 0),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    topics TEXT[],
    title_embedding vector(1536),
    content_embedding vector(1536),
    rating FLOAT CHECK (rating >= 0 AND rating <= 5),
    view_count INTEGER CHECK (view_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create learning goals table
CREATE TABLE IF NOT EXISTS learning_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    target_skills TEXT[] NOT NULL,
    timeframe_weeks INTEGER NOT NULL CHECK (timeframe_weeks > 0),
    difficulty_level VARCHAR(20) DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    goal_embedding vector(1536),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
    progress_percentage FLOAT DEFAULT 0.0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user interactions table
CREATE TABLE IF NOT EXISTS user_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID REFERENCES content_sources(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN ('viewed', 'liked', 'completed', 'bookmarked', 'skipped', 'rated')),
    rating FLOAT CHECK (rating >= 1 AND rating <= 5),
    time_spent_minutes INTEGER CHECK (time_spent_minutes >= 0),
    completion_percentage FLOAT CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    goal_id UUID REFERENCES learning_goals(id) ON DELETE CASCADE,
    content_id UUID REFERENCES content_sources(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    preference_score FLOAT NOT NULL CHECK (preference_score >= 0 AND preference_score <= 1),
    final_score FLOAT NOT NULL CHECK (final_score >= 0 AND final_score <= 1),
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_learning_preferences_user_id ON learning_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_content_sources_content_type ON content_sources(content_type);
CREATE INDEX IF NOT EXISTS idx_content_sources_difficulty ON content_sources(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_content_sources_platform ON content_sources(source_platform);
CREATE INDEX IF NOT EXISTS idx_learning_goals_user_id ON learning_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_goals_status ON learning_goals(status);
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_content_id ON user_interactions(content_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_goal_id ON recommendations(goal_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_final_score ON recommendations(final_score DESC);

-- Create vector similarity indexes for pgvector
CREATE INDEX IF NOT EXISTS idx_content_embedding ON content_sources USING ivfflat (content_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_title_embedding ON content_sources USING ivfflat (title_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_goal_embedding ON learning_goals USING ivfflat (goal_embedding vector_cosine_ops) WITH (lists = 100);
