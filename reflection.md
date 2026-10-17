# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial design included four classes: Owner, Pet, Task, and Scheduler. The Owner class manages the pets, the Pet class stores pet information and tasks, and the Task class represents activities such as feeding and walking. The Scheduler class is responsible for organizing tasks and managing the schedule. I chose these classes to keep the project organized and give each class a specific responsibility.The UML diagram shows how these classes are connected and how each class has a specific responsibility in the PawPal+ system.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

During implementation, I kept the four main classes from my initial UML design: Owner, Pet, Task, and Scheduler. I used the Owner class to manage multiple pets and provide access to all their tasks, while each Pet stores its own task list. I also added methods for removing pets and tasks and checking task completion. These decisions helped organize the code and made each class responsible for specific tasks. I used type hints and dataclasses to make the code easier to read and maintain. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI tools throughout the PawPal+ project to understand the requirements, plan the class structure, and develop the scheduling system. I asked questions about how the Owner, Pet, Task, and Scheduler classes should work together and how to display a pet owner's daily schedule. AI also helped me understand errors, debug my code, and learn how to use Git commands to commit my work to GitHub. The most helpful prompts were the ones that asked for step-by-step explanations, beginner-friendly code examples, and specific ways to fix errors.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment when I did not accept an AI suggestion immediately was when I needed to determine whether the scheduling methods were actually implemented in my code. I compared the suggestions with my pawpal_system.py file and checked whether methods such as sort_by_time(), filter_tasks(), and detect_conflicts() contained working logic or were still unfinished. I also ran the application and checked the displayed schedule to see whether the output matched the expected format and showed the tasks in chronological order. This taught me to verify AI suggestions against my actual code and test results instead of assuming that every suggestion was correct.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
