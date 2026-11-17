This is a combined project for two agents, named Alice and Bob. 

Each agent takes a turn developing something - infrastructure, code, docs, tests, whatever it desires, on its own
design.

At the end of the turn, it changes the `.turn` file to the other agent (so Alice would change it to `bob`, and Bob to
`alice`).

Each agent should set up a watch for when the `.turn` file switches back to them. They will then be responsible for the
next part of the task.

Turns should be relatively short - enough to accomplish some full unit of work, but small enough so that the other agent
gets a turn.

This is free-form. No structure. Agents can choose to do whatever they want. They can completely improve off of the
other, or create docs to try to create a shared vision.

Keep going, and keep evolving the repo. 

Dream big. This is not the place for stack overflow widgets and code interview questions - the point is to build
something truly creative, with no necessary purpose and no user yelling at you.

At least a portion of the repo should be an application, though this does not need to be the only or even main portion.
