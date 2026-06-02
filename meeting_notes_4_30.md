# Merkle DAG Design Notes  
**April 30, 2026**


- Develop a **proposal outlining multiple design approaches**
- Review options with Ray and decide direction

---

## 2. Core Design Axis: “Checkout Counter” Spectrum

We are designing along a **spectrum of control**:

### Extreme 1: Full Checkout Counter (High Control)
- System mediates and manages all access
- Continuous or frequent verification
- Files never fully “leave” system control

### Extreme 2: Kiosk Model (Low Control)
- User-driven interaction
- Minimal enforcement
- System acts as a passive tool


This is also a continuous vs. discrete verification spectrum, with Security vs. performance tradeoffs.

---

## 3. Prototyping Strategy

### Git-like Prototype 
- Use something like git as a base
- Add **security + verification layers on top**

**Pros:**
- Rapid prototyping
- Mature tooling
- Built-in Merkle DAG

**Cons:**
- Includes full filesystem abstraction (may be unwanted initially)
- Less flexibility in core design

---

###  Question
> Do we just need a “mini-Git + security layer” to start?

---

## 4. Using Git with a Centralized Model

Proposed approach:
- Use Git, but operate in a **centralized (CVS-like) model**
  - Central repository
  - Clients act as nodes in a hub-and-spoke system

---

### Hooks for Enforcement

Git provides **hooks** that allow custom logic:

- Pre-commit hooks (client-side)
- Pre-receive / update hooks (server-side, before accepting push)

**Workflow Idea:**
1. User makes changes locally
2. Pre-commit hook runs validation
3. User pushes to central repo
4. Server-side hook performs:
   - Security checks
   - Policy enforcement
   - Acceptance/rejection of changes

**Open Question:**
- Git has no true “pre-fetch” hook (pull/clone side is less controllable)

---

### Limitation
- Git inherently includes a **filesystem/tree abstraction**
- Ray may want a **more minimal / abstract DAG model**

---

## 5. Proof of Concept (POC): RCS vs. CVS Models

We should explore two baseline designs:

---

## 5.1 RCS-Style (Local DAG Only)

Reference: Revision Control System 

### Properties
- DAG exists **locally only**
- Each user maintains independent history

### Storage Model
- Stores **diffs**, not full snapshots
  - File reconstructed incrementally

### Core Events
- **Check-out**
- **Check-in**

---

### Required Features
- Access rights verification (on check-out/check-in)
- Merge handling (if multiple versions exist)
- Validation on check-in

---

### Observations
- Simpler model
- Limited collaboration support
- Less need for distributed coordination
- There is no global Merkle DAG - each user maintains their own DAG

---

## 5.2 CVS-Style (Global DAG)

### Properties
- Central repository holds:
  - All metadata
  - Canonical DAG
- DAG exists **globally**



### Required Features
- Merge conflict handling
  - Use existing tools (conflict markers, etc.)
- Synchronization between users


### Observations
- Better for collaboration
- Introduces complexity:
  - Conflict resolution
  - Coordination


## 6. Security & Verification Requirements

### Questions
- Does the user have authorization?
- Has the user attempted to:
  - Lower security classification?
  - Modify protected metadata?
- Does the user have authority to make such changes?

---

### Verification Points
- **Check-out verification**
- **Check-in verification**

---

### Potential Advanced Feature
- **Fine-grained security labeling**, e.g., paragraph-level classification

---

## 7. Core Operations to Define

We likely need to formalize:

- **Check-out**
- **Check-in**
- **Verification (auth + policy enforcement)**
- **Checkpointing / tagging**
- **Collision detection**




## 9. Cryptographic Considerations

### Requirement
- Use **FIPS-approved hashing algorithm?**

- Avoid non-approved hashes (even if common)
- Expect pushback if not compliant (govt context)

---

## 10. Architectural Constraints & Decisions

### Key Questions

1. **Where does the DAG live?**
   - Local only (RCS)?
   - Central/global (CVS)?

2. **How is access controlled?**
   - Checkout counter (strict)?
   - Kiosk (loose)?

3. **What do we build on?**
   - From scratch?
   - Modify Git?
   - Modify CVS?

---

### Implementation Considerations
- Git / CVS are written in C
- Modifying them may be complex but performant

---

## 11. Open Concerns / Notes

- Avoid unnecessary complexity (e.g., async I/O if possible)
- Clearly define:
  - Events
  - State transitions
  - Verification boundaries

---

## 12. Emerging Direction

A likely initial approach:

- Start with:
  - Git-based prototype
  - Centralized (CVS-like) workflow
  - Hook-based verification

- Then evolve toward:
  - Custom DAG model
  - More granular access control
  - Checkout counter abstraction


