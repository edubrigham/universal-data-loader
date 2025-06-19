Stage Gate Prompt: Implementation Kick-off

Context: A feature folder, including planning documents, has been moved into 
the implementation stage and the folder is referenced in this chat

Instructions:

1.  Analyze Plan: Read and understand the contents of the feature folder,
    focusing on `README.md`, `spec.md`, and `design.md`.
2.  Generate Task List: Based on the spec and design, generate a high-level 
    checklist of the main implementation tasks required to build this feature. 
    Phrase tasks clearly (e.g., "Set up database schema changes", 
    "Build API endpoint for X", "Create frontend component Y", "Write unit tests for Z").
    Save that task list into the attached folder as task_list.md
3.  Suggest Tracking: Recommend creating an `implementation_notes.md` 
    file within the feature folder to track detailed progress, technical 
    decisions, challenges encountered.
4.  Output: Provide the generated task checklist and the suggestion for creating `implementation_notes.md`.

Note
Once you have created the plan, then go ahead and implement this, I expect this
to be a long chain of requests and that you will use a number of tool calls to
achieve this.