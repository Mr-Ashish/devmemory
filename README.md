# devmemory: Continuous Knowledge Extraction for AI-Native Software Development

> Built on the **Hermes** extraction engine — a local transcript-to-knowledge pipeline.

# Vision

Treat documentation as a continuously generated artifact of development rather than something developers manually maintain.

AI coding agents generate an enormous amount of valuable engineering knowledge while helping developers write software. Today, almost all of that knowledge disappears when the session ends. The code survives, but the reasoning behind it is lost.

devmemory changes this by continuously extracting durable knowledge from the development process and turning it into living repository memory.

---

# The Problem

While working with Claude Code, Codex, Gemini CLI, or similar coding agents, developers naturally generate valuable project knowledge:

* Architecture decisions
* Implementation rationale
* Trade-offs
* Debugging journeys
* Commands executed
* APIs explored
* Coding conventions
* Reusable implementation patterns
* Lessons learned
* Project-specific context

Today, this knowledge lives only temporarily:

* Inside developers' heads
* Inside AI conversations
* Inside local session transcripts

Once the work is merged, almost all of it disappears.

The repository preserves the implementation—but not the engineering knowledge that produced it.

---

# The Design

devmemory runs **locally** on the developer's machine alongside Claude Code, powered by the Hermes extraction engine.

Since Claude Code session transcripts (`.jsonl`) never leave the developer's machine, devmemory performs knowledge extraction where the data already exists.

As the developer works—or when a session completes—devmemory:

1. Reads the latest Claude Code session transcripts.
2. Reads the repository being actively developed.
3. Identifies durable knowledge worth preserving.
4. Maps that knowledge to the appropriate location within the repository.
5. Updates the relevant knowledge files automatically.
6. The developer reviews the generated changes just like any other source code change before committing.

No raw transcripts are committed to Git. No private conversations leave the developer's machine.

---

# Context Lives Beside the Code

The core design principle is simple:

> **Knowledge should live as close as possible to the code it describes.**

Instead of maintaining a single, monolithic AI context file for the entire repository, devmemory creates and maintains localized knowledge files throughout the project.

For example:

```text
odoo/
├── addons/
│   ├── sales/
│   │   ├── DEV.md
│   │   ├── USAGE.md
│   │   ├── models/
│   │   └── services/
│   │
│   ├── accounting/
│   │   ├── DEV.md
│   │   ├── USAGE.md
│   │   └── ...
│   │
│   └── inventory/
│       ├── DEV.md
│       ├── USAGE.md
│       └── ...
│
├── shared/
│   ├── DEV.md
│   └── USAGE.md
│
└── DEV.md
```

Every significant module, package, or subsystem can have its own local knowledge.

When Claude Code begins working inside a directory, it naturally discovers these files alongside the source code.

This gives the coding agent immediate access to the exact context it needs without searching across the entire repository.

---

# AI-Native Repository Memory

devmemory continuously maintains two complementary knowledge files.

## DEV.md

`DEV.md` captures durable engineering knowledge, including:

* Architecture
* Design decisions
* Repository conventions
* Coding patterns
* Important implementation details
* Common pitfalls
* Module-specific context
* Extension points

This answers the question:

> **"How is this part of the system built?"**

---

## USAGE.md

`USAGE.md` captures operational knowledge that helps developers and AI agents work efficiently.

Examples include:

* Copy-pasteable build commands
* Test commands
* Debugging commands
* Local development workflows
* Deployment commands
* Frequently used scripts
* Module-specific setup
* Common troubleshooting procedures
* AI workflow instructions

This answers the question:

> **"How do I work with this part of the system?"**

Instead of asking an AI:

> "How do I run the accounting tests?"

Claude Code can immediately read the local `USAGE.md` sitting next to the accounting module and execute the correct commands.

---

# Continuous Knowledge Extraction Pipeline

During development, devmemory continuously transforms ephemeral AI conversations into permanent repository knowledge.

For every meaningful development session, devmemory:

1. Reads the latest Claude Code transcripts.
2. Reads the current code changes.
3. Infers what durable knowledge was created.
4. Determines which module or directory that knowledge belongs to.
5. Updates only the relevant local `DEV.md` and `USAGE.md` files.
6. Presents the generated documentation changes alongside the code changes.
7. The developer commits both the implementation and the updated repository knowledge together.

GitHub Actions never needs access to local transcripts.

Instead, CI simply validates that the generated knowledge files are well-formed, consistent, and up to date.

---

# The Fundamental Shift

Developers shouldn't have to stop building software to document what they just built.

Instead:

> **Developers build software. devmemory continuously extracts engineering knowledge from the development process and stores it exactly where future developers and AI agents will need it.**

Documentation becomes a natural by-product of development rather than a separate task.

---

# Why Localized Knowledge Matters

Large repositories contain thousands of files.

A single repository-wide context document quickly becomes:

* Too large
* Too generic
* Difficult to maintain
* Expensive for AI agents to consume

By colocating knowledge with the code it describes:

* Developers immediately find relevant documentation.
* Claude Code loads only the context relevant to the files being edited.
* Context windows are used more efficiently.
* Commands are already available where they're needed.
* Repository knowledge scales naturally as the project grows.

The repository effectively becomes self-describing.

---

# Compounding Repository Intelligence

Over weeks and months, every directory develops its own evolving memory:

* Architectural history
* Engineering decisions
* Coding conventions
* Reusable implementation patterns
* Copy-pasteable workflows
* Build and test commands
* Troubleshooting knowledge
* AI operating instructions

Every development session enriches the repository.

Every debugging session becomes reusable.

Every architectural decision becomes discoverable.

Every workflow becomes executable without rediscovery.

---

# Long-Term Vision

Future developers should inherit not only the code but also the thinking behind it.

Future AI coding agents should not start every session from scratch. They should begin with localized, high-quality context that lives directly beside the code they are modifying.

devmemory transforms transient AI conversations into durable, version-controlled repository memory.

The result is an AI-native repository where every directory contains both the implementation and the knowledge required to understand, extend, test, and operate it. As the software evolves, so does its memory.