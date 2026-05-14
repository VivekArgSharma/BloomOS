PlantIQ — Product Requirements Document (PRD)
Product Name
PlantIQ — AI-Powered Personalized Plant Intelligence System

1. Executive Summary
PlantIQ is an AI-powered smart gardening platform that helps users manage plant care intelligently using Computer Vision, AI planning systems, RAG-based contextual reasoning, and climate-aware recommendations.
Unlike traditional gardening apps that provide static reminders and generic advice, PlantIQ continuously learns from each plant’s visual health, historical growth, environmental conditions, and user behavior to generate adaptive care plans and intelligent recommendations.
The platform acts as a personalized AI doctor for plants.

“Most apps treat every Monstera the same. PlantIQ learns YOUR Monstera.”


2. Problem Statement
Urban gardening and indoor plant culture are growing rapidly, but maintaining healthy plants remains difficult due to:


Lack of plant care knowledge


Incorrect watering schedules


Delayed disease detection


Poor climate awareness


No personalized guidance


Generic internet advice


Inconsistent monitoring


Most existing solutions only provide:


Basic plant identification


Static reminders


Generic care guides


They do not:


Learn plant history


Adapt plans dynamically


Use daily visual feedback


Personalize recommendations


Predict health decline


Understand environmental context


PlantIQ solves this using adaptive AI-driven monitoring and intelligent care planning.

3. Vision
To build the world’s most intelligent personalized plant care assistant that evolves with every plant over time.

4. Objectives
Primary Objectives


Reduce plant mortality


Simplify gardening for beginners


Enable AI-driven plant monitoring


Provide adaptive personalized care


Improve sustainable urban gardening


Demonstrate advanced AI workflows


Secondary Objectives


Gamify plant care


Improve user consistency


Build long-term garden analytics


Create emotional user engagement through plant diaries



5. User Personas
Beginner Plant Owner
Needs:


Simple instructions


Disease detection


Watering guidance


Beginner-friendly UI


Pain Points:


Overwatering


Cannot identify diseases


Doesn’t know plant species



Hobby Gardener
Needs:


Multi-plant management


Growth tracking


Garden health analytics


Climate-aware insights



Balcony/Terrace Garden Enthusiast
Needs:


Ecosystem-level monitoring


Seasonal planning


Weather-aware recommendations



6. Product Structure
User
└── Gardens
  └── Plants
    └── Daily Logs

7. Core Features
7.1 Multi-Garden Management
Users can create multiple gardens.
Examples:


Balcony Garden


Living Room Garden


Terrace Garden


Indoor Garden


Each garden contains:


Multiple plants


Overall health score


Environmental context


Daily task summaries


Alerts and warnings


Garden Health Calculation
Average of all plant health scores.
Status:


90–100 → Thriving


70–89 → Good


50–69 → Needs Attention


Below 50 → Critical



7.2 Plant Onboarding
Method A — AI Image Identification
User uploads a plant image.
Gemini Vision:


Identifies species


Generates care profile


Detects difficulty level


Creates care metadata



Method B — Plant Catalog Search
Users can choose from ~50 popular plants.
Examples:


Monstera


Snake Plant


Tulsi


Aloe Vera


Peace Lily


Hibiscus


Rose


Pothos


Benefits:


Faster onboarding


Reduced API usage


Offline-friendly


Lower cost



7.3 AI-Generated 30-Day Care Plans
After onboarding, the system generates:


Watering schedules


Fertilizer plans


Sunlight recommendations


Monitoring tasks


Preventive care routines


Inputs used:


Plant species


Weather forecast


Garden type


User location


Historical health trends


Plant difficulty


Plans are adaptive and continuously updated.

7.4 Daily AI Task Engine
Every day the system generates contextual tasks.
Examples:


Water today


Skip watering due to rain


Rotate plant for sunlight


Check leaves for pests


Upload progress photo


Inputs:


Weather data


Last watering date


Health history


User completion behavior


Vision analysis results



7.5 Daily Photo Analysis
Users upload daily photos.
Gemini Vision analyzes:


Leaf condition


Yellowing


Wilting


Soil appearance


Disease symptoms


Growth progression


Returns:


Health score (1–10)


Visible issues


Soil moisture estimate


Urgency flag


Recommended actions


Example Output:
{  "health_score": 8,  "visible_issues": ["minor yellowing"],  "soil_moisture": "adequate",  "recommended_action": "continue current watering schedule",  "flag_urgent": false}

7.6 Adaptive Plan Modification
The system compares:


Previous health trends


Current analysis


Weather conditions


User care consistency


If decline is detected:


Watering intervals are adjusted


Monitoring increases


Recovery mode activates


Daily tasks are modified



7.7 Recovery Mode
Activated when:


Health score < 5


Features:


Intensive monitoring


Daily photo requests


Specialized recovery plans


Urgent notifications


Disease-specific recommendations



7.8 Disease Early Warning System
Tracks health score trends over time.
Example:
8 → 7 → 6
The system raises alerts even before severe visible symptoms appear.
Goal:
Predict problems early and reduce plant mortality.

7.9 Visual Health Timeline
Stores:


Daily photos


Health scores


AI observations


Historical analyses


Users can:


View growth progression


Compare recovery over time


Analyze plant health visually



7.10 Plant Diary
Every analysis becomes a human-readable diary entry.
Example:

“Day 14: New growth observed near stem. Yellowing has reduced significantly. Health improving steadily.”


7.11 Contextual AI Chatbot
Users can ask:


Why are leaves curling?


Why is my plant drooping?


Should I water today?


Responses use:


Plant history


Recent photos


Weather context


Health trends


RAG-based retrieval



7.12 RAG-Based Plant Knowledge System
The system uses Retrieval-Augmented Generation (RAG) for grounded responses.
Knowledge Sources


Plant care guides


Disease references


Soil recommendations


Watering best practices


Fertilizer information


Seasonal gardening data


Vector Database
FAISS
Embeddings
sentence-transformers
Workflow
User Question
→ Query Embedding
→ FAISS Retrieval
→ Relevant Chunks
→ Gemini Prompt Context
→ Grounded AI Response
Benefits:


Reduced hallucinations


Improved accuracy


Reliable recommendations


Contextual reasoning



7.13 Weather Integration
Uses OpenWeatherMap API for:


Temperature


Humidity


Rain forecasts


UV index


Seasonal trends


Example:

“Rain expected tomorrow — skip watering today.”


7.14 Soil Health Inference Engine
No IoT hardware required.
The system estimates soil condition using:


Pot size


Weather conditions


Days since watering


Plant species


Humidity levels


This simulates smart sensing without hardware.

7.15 Plant Compatibility Checker
Before adding a plant, the system evaluates:


Humidity compatibility


Sunlight compatibility


Space suitability


Climate compatibility


Example:

“Your balcony currently supports high-humidity plants. Desert cactus may struggle here.”


7.16 Gamification
Features:


Streaks


Achievement badges


Progress tracking


Care heatmaps


Examples:


7-Day Streak


Disease Survivor


Green Thumb


Perfect Garden



7.17 Beginner Mode
Simplified interface for new users.
Features:


Reduced complexity


Friendly explanations


Guided onboarding


Educational tips



8. Technical Architecture
Frontend


React


Tailwind CSS


Framer Motion


React Query


Backend


FastAPI


Python


AI Layer


Gemini 1.5 Flash / Gemini Flash Lite


Agent Framework


LangGraph


Vector Database


FAISS


Embedding Model


sentence-transformers


Database


Supabase PostgreSQL


Storage


Supabase Storage


Hosting
Frontend:


Vercel


Backend:


Render



9. AI System Pipelines
Pipeline 1 — Plant Identification
Image Upload
→ Gemini Vision
→ Species Detection
→ Care Profile Generation
→ Database Storage

Pipeline 2 — Daily Health Analysis
Photo Upload
→ Gemini Vision
→ Health Analysis
→ Trend Comparison
→ Plan Adjustment
→ Database Update

Pipeline 3 — RAG Chat System
User Question
→ Embedding Generation
→ FAISS Retrieval
→ Context Injection
→ Gemini Response

Pipeline 4 — Daily Planner Agent
Inputs:


Weather data


Health history


User behavior


Care plans


Vision analysis


Outputs:


Daily tasks


Alerts


Recovery recommendations


Plan modifications



10. LangGraph Agent Workflow
Nodes:


Load Plant Context


Fetch Weather


Fetch Health Trends


Retrieve RAG Context


Generate Daily Tasks


Evaluate Risks


Modify Plans


Save Updated State



11. Database Schema
Users


id


name


email


city


created_at



Gardens


id


user_id


garden_name


location_type


created_at



Plants


id


garden_id


common_name


species_name


care_profile


current_health_score


added_via


recovery_mode


created_at



DailyLogs


id


plant_id


photo_url


health_score


observations


tasks_completed


analysis_json


created_at



DailyPlans


id


plant_id


date


tasks


weather_snapshot


generated_by_ai



PlantCatalog


id


common_name


species_name


care_profile


difficulty


tags



12. Caching Strategy
Caching is critical due to Gemini free-tier limitations.
Goals


Reduce API calls


Improve response speed


Prevent rate limits


Lower operational costs



12.1 Plant Catalog Caching
Pre-generate care profiles for catalog plants and store permanently in the database.
No runtime AI calls required.

12.2 Prompt Result Caching
If:


Same image hash


Same question


Same plant state


Then:


Return cached response


Possible technologies:


Redis


In-memory cache


Supabase cache tables



12.3 Weather Caching
Weather data cached for 1–3 hours to minimize API requests.

12.4 Embedding Caching
Store embeddings permanently.
Do not regenerate existing embeddings.

12.5 RAG Optimization
FAISS index built offline and shipped with backend deployment.
Only query embeddings are generated dynamically.

12.6 Image Compression Pipeline
Before Gemini analysis:


Resize image


Compress image


Strip metadata


Benefits:


Faster uploads


Lower token usage


Faster inference



13. API Rate Limit Optimization
Gemini API calls only for:


Plant onboarding


Daily photo analysis


Plan updates


Contextual Q&A


Avoid AI calls for:


Static care profiles


Cached analyses


Catalog information


Repeated queries



14. Security & Privacy
Stored Data


Plant photos


Health logs


Garden information


User preferences


Security Measures


Supabase Authentication


JWT tokens


Secure image uploads


Environment variable protection


Signed URLs



15. Performance Goals
Image Upload
Target:
< 3 seconds
AI Analysis
Target:
< 7 seconds
Dashboard Loading
Target:
< 2 seconds

16. Future Scope
Potential future features:


AR plant placement visualization


IoT sensor integration


Voice assistant


Multilingual support


Community gardening platform


Growth prediction models


Pest segmentation models


Smart irrigation hardware


Offline edge AI



17. Hackathon MVP Scope
Must Have


Multi-garden system


Plant onboarding


AI plant identification


Daily AI tasks


Photo analysis


Adaptive planning


Weather integration


RAG chatbot


Dashboard analytics



Should Have


Visual timelines


Recovery mode


Gamification


Garden health scoring


Plant diary



Nice To Have


Compatibility checker


Seasonal adaptation


Predictive alerts


AR visualization mockup



18. Demo Flow


User creates a garden


User uploads a plant image


AI identifies species


AI generates care plan


Dashboard displays health and tasks


User uploads progress photo


AI updates recommendations


Show visual timeline


Demonstrate contextual chatbot


Explain RAG architecture



19. Key Differentiators
What makes PlantIQ unique:


Adaptive personalized plans


Daily multimodal reasoning


Long-term plant memory


Weather-aware intelligence


RAG-grounded recommendations


Predictive health analysis


Multi-garden ecosystem monitoring


Vision-driven progression tracking


Software-defined sensing



20. Success Metrics
Product Metrics


Daily active users


Task completion rate


Health improvement trends


User retention


Upload consistency


Technical Metrics


AI response accuracy


Cache hit rate


API efficiency


Retrieval relevance


Plan adaptation quality



21. Elevator Pitch
PlantIQ is an AI-powered personalized plant intelligence platform that continuously learns from each plant’s visual health, care history, local climate, and user behavior to generate adaptive care plans and contextual recommendations.
Instead of static reminders, PlantIQ evolves with your plants over time using multimodal AI, RAG-based reasoning, weather-aware planning, and intelligent monitoring.

22. Final Positioning Statement
PlantIQ is not a plant reminder app.
It is a continuously learning AI ecosystem for personalized plant health management.