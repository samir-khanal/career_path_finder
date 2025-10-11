/*
  # Resume Analyzer Database Schema

  ## Overview
  This migration creates the complete database structure for the Resume Analyzer application,
  including tables for user management, resume storage, skill tracking, and job role definitions.

  ## New Tables Created

  ### 1. `users` - User Authentication and Profile
    - `id` (uuid, primary key) - Unique user identifier
    - `email` (text, unique) - User email address
    - `full_name` (text) - User's full name
    - `created_at` (timestamptz) - Account creation timestamp
    - `last_login` (timestamptz) - Last login timestamp

  ### 2. `resumes` - Uploaded Resume Storage
    - `id` (uuid, primary key) - Unique resume identifier
    - `user_id` (uuid, foreign key) - References users table
    - `filename` (text) - Original filename
    - `file_type` (text) - PDF or DOCX
    - `raw_text` (text) - Extracted text content
    - `parsed_skills` (jsonb) - Array of extracted skills
    - `parsed_education` (jsonb) - Array of education entries
    - `parsed_experience` (jsonb) - Array of experience entries
    - `upload_date` (timestamptz) - Upload timestamp
    - `file_size` (integer) - File size in bytes

  ### 3. `job_roles` - Career Path Definitions
    - `id` (uuid, primary key) - Unique role identifier
    - `role_name` (text, unique) - Job role name (e.g., "Data Scientist")
    - `required_skills` (jsonb) - Array of required skills
    - `description` (text) - Role description
    - `category` (text) - Role category (Tech, Management, etc.)
    - `experience_level` (text) - Junior, Mid, Senior
    - `created_at` (timestamptz) - Creation timestamp
    - `updated_at` (timestamptz) - Last update timestamp

  ### 4. `skill_gaps` - Analysis Results
    - `id` (uuid, primary key) - Unique analysis identifier
    - `resume_id` (uuid, foreign key) - References resumes table
    - `user_id` (uuid, foreign key) - References users table
    - `target_role` (text) - Target job role analyzed
    - `matched_skills` (jsonb) - Array of matched skills
    - `missing_skills` (jsonb) - Array of missing skills
    - `match_score` (numeric) - Percentage match score
    - `analysis_date` (timestamptz) - Analysis timestamp

  ### 5. `skills_database` - Comprehensive Skills Repository
    - `id` (uuid, primary key) - Unique skill identifier
    - `skill_name` (text, unique) - Normalized skill name
    - `category` (text) - Skill category (Programming, Database, etc.)
    - `synonyms` (jsonb) - Array of skill synonyms
    - `popularity_score` (integer) - Skill demand score (1-100)
    - `last_updated` (timestamptz) - Last update timestamp

  ## Security
  - Row Level Security (RLS) enabled on all tables
  - Users can only access their own data
  - Authenticated users required for all operations

  ## Indexes
  - Created on foreign keys for performance
  - Created on commonly queried fields
*/

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: users
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  full_name text,
  created_at timestamptz DEFAULT now(),
  last_login timestamptz DEFAULT now()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- =====================================================
-- TABLE: resumes
-- =====================================================
CREATE TABLE IF NOT EXISTS resumes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename text NOT NULL,
  file_type text NOT NULL CHECK (file_type IN ('pdf', 'docx')),
  raw_text text,
  parsed_skills jsonb DEFAULT '[]'::jsonb,
  parsed_education jsonb DEFAULT '[]'::jsonb,
  parsed_experience jsonb DEFAULT '[]'::jsonb,
  upload_date timestamptz DEFAULT now(),
  file_size integer DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_upload_date ON resumes(upload_date DESC);

ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own resumes"
  ON resumes FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own resumes"
  ON resumes FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own resumes"
  ON resumes FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own resumes"
  ON resumes FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- =====================================================
-- TABLE: job_roles
-- =====================================================
CREATE TABLE IF NOT EXISTS job_roles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  role_name text UNIQUE NOT NULL,
  required_skills jsonb DEFAULT '[]'::jsonb,
  description text,
  category text DEFAULT 'General',
  experience_level text DEFAULT 'Mid' CHECK (experience_level IN ('Junior', 'Mid', 'Senior', 'Lead')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_roles_category ON job_roles(category);
CREATE INDEX IF NOT EXISTS idx_job_roles_experience ON job_roles(experience_level);

ALTER TABLE job_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view job roles"
  ON job_roles FOR SELECT
  TO authenticated
  USING (true);

-- =====================================================
-- TABLE: skill_gaps
-- =====================================================
CREATE TABLE IF NOT EXISTS skill_gaps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id uuid NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_role text NOT NULL,
  matched_skills jsonb DEFAULT '[]'::jsonb,
  missing_skills jsonb DEFAULT '[]'::jsonb,
  match_score numeric(5,2) DEFAULT 0.0 CHECK (match_score >= 0 AND match_score <= 100),
  analysis_date timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_skill_gaps_resume_id ON skill_gaps(resume_id);
CREATE INDEX IF NOT EXISTS idx_skill_gaps_user_id ON skill_gaps(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_gaps_date ON skill_gaps(analysis_date DESC);

ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own skill gaps"
  ON skill_gaps FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own skill gaps"
  ON skill_gaps FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- TABLE: skills_database
-- =====================================================
CREATE TABLE IF NOT EXISTS skills_database (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_name text UNIQUE NOT NULL,
  category text NOT NULL,
  synonyms jsonb DEFAULT '[]'::jsonb,
  popularity_score integer DEFAULT 50 CHECK (popularity_score >= 0 AND popularity_score <= 100),
  last_updated timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_skills_category ON skills_database(category);
CREATE INDEX IF NOT EXISTS idx_skills_popularity ON skills_database(popularity_score DESC);

ALTER TABLE skills_database ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view skills database"
  ON skills_database FOR SELECT
  TO authenticated
  USING (true);

-- =====================================================
-- SEED DATA: Insert default job roles
-- =====================================================
INSERT INTO job_roles (role_name, required_skills, description, category, experience_level) VALUES
  (
    'Junior Data Scientist',
    '["Python", "Pandas", "NumPy", "Data Visualization", "SQL", "Statistics", "Scikit-learn", "EDA", "Machine Learning"]'::jsonb,
    'Entry-level data scientist focused on data analysis and basic ML models',
    'Data Science',
    'Junior'
  ),
  (
    'Senior Data Scientist',
    '["Python", "Advanced Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Big Data", "Spark", "Cloud Platforms", "MLOps", "Leadership"]'::jsonb,
    'Experienced data scientist leading projects and mentoring junior team members',
    'Data Science',
    'Senior'
  ),
  (
    'Data Analyst',
    '["SQL", "Excel", "Data Visualization", "Tableau", "Power BI", "Statistics", "Python", "Pandas", "Reporting"]'::jsonb,
    'Analyze data and create reports to support business decisions',
    'Data Analytics',
    'Mid'
  ),
  (
    'Machine Learning Engineer',
    '["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "MLOps", "Docker", "Kubernetes", "AWS", "Model Deployment"]'::jsonb,
    'Build and deploy production ML systems at scale',
    'Machine Learning',
    'Mid'
  ),
  (
    'Full Stack Developer',
    '["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL", "Git", "REST APIs", "MongoDB", "TypeScript"]'::jsonb,
    'Develop complete web applications from frontend to backend',
    'Software Development',
    'Mid'
  ),
  (
    'Frontend Developer',
    '["JavaScript", "React", "HTML", "CSS", "TypeScript", "Redux", "Webpack", "Responsive Design", "Git", "REST APIs"]'::jsonb,
    'Create user interfaces and client-side applications',
    'Software Development',
    'Junior'
  ),
  (
    'Backend Developer',
    '["Python", "Node.js", "Java", "SQL", "PostgreSQL", "REST APIs", "Docker", "Git", "Redis", "Microservices"]'::jsonb,
    'Build server-side applications and APIs',
    'Software Development',
    'Mid'
  ),
  (
    'DevOps Engineer',
    '["AWS", "Docker", "Kubernetes", "CI/CD", "Jenkins", "Terraform", "Git", "Linux", "Python", "Monitoring"]'::jsonb,
    'Automate infrastructure and deployment pipelines',
    'DevOps',
    'Mid'
  ),
  (
    'Cloud Architect',
    '["AWS", "Azure", "GCP", "Cloud Architecture", "Microservices", "Kubernetes", "Terraform", "Security", "Networking", "Cost Optimization"]'::jsonb,
    'Design and implement scalable cloud solutions',
    'Cloud Computing',
    'Senior'
  ),
  (
    'Business Analyst',
    '["SQL", "Excel", "Data Analysis", "Requirements Gathering", "Stakeholder Management", "Agile", "JIRA", "Documentation", "Communication"]'::jsonb,
    'Bridge business needs with technical solutions',
    'Business',
    'Mid'
  )
ON CONFLICT (role_name) DO NOTHING;

-- =====================================================
-- SEED DATA: Insert comprehensive skills database
-- =====================================================
INSERT INTO skills_database (skill_name, category, synonyms, popularity_score) VALUES
  ('Python', 'Programming Languages', '["python", "py", "python3", "python programming"]'::jsonb, 95),
  ('JavaScript', 'Programming Languages', '["javascript", "js", "ecmascript", "es6"]'::jsonb, 98),
  ('Java', 'Programming Languages', '["java", "java programming"]'::jsonb, 85),
  ('SQL', 'Database', '["sql", "mysql", "postgresql", "postgres", "structured query language"]'::jsonb, 90),
  ('React', 'Frontend Framework', '["react", "reactjs", "react.js"]'::jsonb, 92),
  ('Node.js', 'Backend Framework', '["node", "nodejs", "node.js"]'::jsonb, 88),
  ('Machine Learning', 'AI/ML', '["machine learning", "ml", "statistical learning"]'::jsonb, 85),
  ('Deep Learning', 'AI/ML', '["deep learning", "dl", "neural networks"]'::jsonb, 80),
  ('TensorFlow', 'AI/ML Framework', '["tensorflow", "tf"]'::jsonb, 75),
  ('PyTorch', 'AI/ML Framework', '["pytorch", "torch"]'::jsonb, 78),
  ('Pandas', 'Data Science', '["pandas", "pd"]'::jsonb, 82),
  ('NumPy', 'Data Science', '["numpy", "np"]'::jsonb, 80),
  ('Docker', 'DevOps', '["docker", "containerization"]'::jsonb, 88),
  ('Kubernetes', 'DevOps', '["kubernetes", "k8s"]'::jsonb, 82),
  ('AWS', 'Cloud', '["aws", "amazon web services", "amazon aws"]'::jsonb, 90),
  ('Azure', 'Cloud', '["azure", "microsoft azure"]'::jsonb, 75),
  ('Git', 'Version Control', '["git", "github", "gitlab", "version control"]'::jsonb, 95),
  ('REST APIs', 'Web Development', '["rest", "rest api", "restful", "api"]'::jsonb, 85),
  ('Agile', 'Methodology', '["agile", "scrum", "agile methodology"]'::jsonb, 80),
  ('Communication', 'Soft Skills', '["communication", "communication skills", "verbal communication"]'::jsonb, 90)
ON CONFLICT (skill_name) DO NOTHING;
