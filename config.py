# Configuration settings

# Database directory
DATABASE_DIR = 'databases'

# Workspace directory
WORKSPACE_DIR = 'workspace'

# Agent configuration
AGENTS = [
    {
        'name': 'Alice',
        'role': 'Technical Lead that leads software development team',
        'home_pos': (50, 50),
        'office_pos': (300, 200)
    },
    {
        'name': 'Bob',
        'role': 'Backend Developer for projects and applications',
        'home_pos': (50, 150),
        'office_pos': (400, 300)
    },
    {
        'name': 'Carol',
        'role': 'Frontend Developer of user interfaces and experiences',
        'home_pos': (50, 250),
        'office_pos': (500, 400)
    },
    {
        'name': 'David',
        'role': 'Quality Assurance Engineer that tests software applications',
        'home_pos': (50, 350),
        'office_pos': (600, 500)
    },
    {
        'name': 'Eve',
        'role': 'DevOps Engineer that automates software development processes',
        'home_pos': (50, 450),
        'office_pos': (700, 600)
    },
    {
        'name': 'Frank',
        'role': 'Data Scientist that analyzes and interprets complex digital data',
        'home_pos': (50, 550),
        'office_pos': (800, 700)
    }
]

# Simulation settings
SIMULATION_DURATION = 220  # in seconds