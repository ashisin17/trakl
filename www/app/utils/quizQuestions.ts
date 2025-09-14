export const QUIZ_QUESTIONS = [
  {
        id:"visual_1",
        question:"When learning something new, I prefer to:",
        options:[
            {"value": "diagrams", "text": "See diagrams, charts, and visual aids", "category": "visual", "weight": 1.0},
            {"value": "listen", "text": "Listen to explanations and discussions", "category": "auditory", "weight": 1.0},
            {"value": "hands_on", "text": "Try it out hands-on immediately", "category": "kinesthetic", "weight": 1.0},
            {"value": "read", "text": "Read detailed written instructions", "category": "reading", "weight": 1.0}
        ],
        category:"learning_style"
    },
    {
        id:"content_type_1",
        question:"For learning programming, I find most helpful:",
        options:[
            {"value": "video_tutorials", "text": "Video tutorials with screen recordings", "category": "video", "weight": 1.0},
            {"value": "written_guides", "text": "Written tutorials and documentation", "category": "article", "weight": 1.0},
            {"value": "interactive_coding", "text": "Interactive coding exercises", "category": "interactive", "weight": 1.0},
            {"value": "structured_course", "text": "Structured online courses", "category": "course", "weight": 1.0}
        ],
        category:"content_type"
    },
    {
        id:"visual_2",
        question:"When I need to remember information, I:",
        options:[
            {"value": "visualize", "text": "Create mental pictures or mind maps", "category": "visual", "weight": 0.8},
            {"value": "repeat", "text": "Repeat it out loud or in my head", "category": "auditory", "weight": 0.8},
            {"value": "write_practice", "text": "Write it down and practice", "category": "kinesthetic", "weight": 0.8},
            {"value": "organize_notes", "text": "Organize it in detailed notes", "category": "reading", "weight": 0.8}
        ],
        category:"learning_style"
    },
    {
        id:"difficulty_pref",
        question:"I prefer learning materials that are:",
        options:[
            {"value": "beginner", "text": "Step-by-step from the basics", "category": "difficulty", "weight": 1.0},
            {"value": "intermediate", "text": "Moderately challenging with some prior knowledge", "category": "difficulty", "weight": 1.0},
            {"value": "advanced", "text": "Advanced and assume strong fundamentals", "category": "difficulty", "weight": 1.0}
        ],
        category:"difficulty"
    },
    {
        id:"session_length",
        question:"My ideal learning session length is:",
        options:[
            {"value": "15", "text": "15-20 minutes (quick focused bursts)", "category": "session", "weight": 1.0},
            {"value": "30", "text": "30-45 minutes (moderate sessions)", "category": "session", "weight": 1.0},
            {"value": "60", "text": "60+ minutes (deep dive sessions)", "category": "session", "weight": 1.0}
        ],
        category:"session_length"
}];