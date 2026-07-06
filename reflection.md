# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    <3 core actions a user can do>:
        1. Add a pet (type, species, name..)
        2. schedule a task (e.g. walking, feeding, )
        3. see today's task (e.g. notification, checklist)

- What classes did you include, and what responsibilities did you assign to each?
Four required classes: Owner, Pet, Task, Scheduler
Brainstorm: probably some type of a customized object for pet, 
        with attributes of type, species, name, 
        and a vector or some type of list for holding and accessing daily tasks
     - methods for viewing these attributes
     - methods for changing these attributes, with some type of access control for users
     - methods for displaying the daily task
     - methods for adding, removing or modifying task into the list of daily task
     


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
