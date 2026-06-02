# 🧠 Merkle DAG Design Notes  
**Meeting with James — April 29, 2026**

---

## 1. Git as a Reference Model for a Content-Addressed Filesystem

### Core Idea: “Git the Filesystem”
- In Git (version control system), every node (repository clone) contains a **complete copy of all data**.
- Data is stored as **content-addressed objects**, identified by hashes (historically SHA-1).
- The system behaves like a **Merkle DAG**:
  - Each object (blob, tree, commit) references others by hash.
  - The full structure forms a directed acyclic graph.

### Object Storage Details
- Each object is stored as a file:
  - Filename = hash of its contents
  - Directory structure:
    - First 2 characters → directory
    - Remaining characters → filename

- Example: abcd1234... → stored as .git/objects/ab/cd1234...


### Entry Points into the DAG
- The raw object graph is not directly navigated by users.
- Instead, Git provides **entry points**:
- **Branches**: mutable pointers to commits
- **Tags**: fixed (usually immutable) pointers to commits

**Q: Why is a tag an entry point?**  
A tag is a named reference to a specific object (typically a commit). It serves as a **stable root** from which the DAG can be traversed—just like a branch, but without moving over time.

---

### Garbage Collection (Clarified)
This likely refers to **mark-and-sweep garbage collection**:
- Start from entry points (branches/tags)
- Mark all reachable objects
- Unmarked objects are garbage and can be deleted

---

### Tree Objects (“Tree-ish”)
- Git maintains structured objects:
- **Blobs** → file contents
- **Trees** → directory structures
- **Commits** → snapshots referencing trees
- “Tree-ish” refers to anything that resolves to a tree (commit, tree, tag, etc.)

---

## 2. User-Driven System

### Definition
“User-driven” means:
- The system only recognizes changes when the user explicitly performs an action (e.g., commit).

### Implications
- Modifications (data, metadata, security attributes) are **not tracked automatically**
- The user must declare:
> “Here is the updated state of this file”

---

### Design Questions
When a user commits a change:
1. **Scope**
 - Local only?
 - Distributed/shared?

2. **Metadata**
 - What security or validation metadata must be attached?
 - How is integrity/authenticity enforced?

3. **Distribution Model**
 - How are updates propagated?

---

## 3. Version Control Models (Design Space)

### 3.1 Local Model (RCS-style)
- Example: Revision Control System (RCS)
- Workflow:
- Modify file
- Check in changes locally
- System creates a new version node
- Properties:
- Fully local
- No inherent synchronization mechanism

---

### 3.2 Centralized Model (CVS-style)
- Example: Concurrent Versions System (CVS)
- Workflow:
- Commit changes to a **central repository**
- Others must:
  - Pull updates
  - Merge before pushing
- Key property:
- **All authoritative metadata lives centrally**

---

### 3.3 Distributed Model (Git-style)
- Hybrid of both:
- Local commits (like RCS)
- Optional push/pull (like CVS)
- Each node:
- Has full history
- Can operate independently

---

## 4. Security vs. Performance Tradeoff

### Core Tension
> “We need to choose between maximum security and minimizing CPU usage.”

This is fundamentally a **continuous vs. discrete verification problem**.

---

### High-Security Model (Continuous Monitoring)
- System continuously verifies permissions and actions
- Example:
- Check access rights ~10 times per second
- Properties:
- Strong guarantees
- Immediate revocation possible
- Cost:
- High CPU overhead
- Potential latency

---

### Low-Overhead Model (Static Access)
- Access is verified **once at open time**
- Example:
- Open file → get file descriptor → retain access indefinitely
- Properties:
- Minimal CPU usage
- Fast
- Risk:
- Permissions may become stale
- No ongoing enforcement

---

### Interpretation
This maps to:
- **Continuous validation** ↔ security
- **Cached authorization** ↔ performance

Analogous to:
- Lease vs. lock models in distributed systems
- Capability vs. ACL checks in OS design

---

## 5. The “Checkout Counter” Abstraction

### Concept
A **middleware layer** between:
- User
- Underlying (black-box) filesystem / DAG

---

### High-Control Model (Strict Enforcement)
- The file never leaves system control
- Workflow:
1. User requests file
2. System provides controlled access
3. On every save:
   - File is revalidated
   - Security policies enforced

**Analogy:**
> Like a checkout counter where you can inspect an item, but never leave the store with it.

---

### Low-Control Model (User-Driven)
- System acts as a **passive tool**
- Files are:
- Retrieved
- Modified freely
- Re-submitted at user discretion

**Analogy:**
> A kiosk off to the side — participation is optional.

---

### Spectrum of Control

| Model | Control Level | Security | Performance |
|------|-------------|--------|------------|
| Checkout Counter (strict) | High | High | Lower |
| Hybrid | Medium | Medium | Medium |
| Kiosk (user-driven) | Low | Lower | High |

---

## 6. FUSE and Copy Control

- FUSE (Filesystem in Userspace) was discussed as a possible mechanism

### Problem
- If users can access raw files, they can:
- Copy (`cp`)
- Exfiltrate data

### Controlled System Advantage
- If all access goes through the “checkout counter”:
- You can:
  - Allow/disallow copying
  - Enforce policies dynamically
- This enables:
- Fine-grained control over file usage
- Policy-driven access

---

## 7. Key Architecture

We are designing along **two orthogonal axes**:

### Axis 1: Data Model
- Merkle DAG (content-addressed, immutable nodes)

### Axis 2: Access Model
- Controlled (mediated, secure)
- vs.
- Uncontrolled (user-driven, flexible)

---

### Design Question
> How tightly should **access control** be coupled to the **Merkle DAG structure**?

This relates
- Capability-based security
- Zero-trust systems
- Distributed state verification

---

## 8. Takeaways / Next Directions

- Git provides a **working blueprint** for:
- Content addressing
- DAG traversal
- Garbage collection

- Design space includes:
- **Access control layer (checkout counter)**
- **Security-performance tradeoffs**
- **Distributed synchronization semantics**

---

### Possible Next Steps?
Formalize:
- Checkout counter as a **state machine over DAG nodes**
- Checkpointing and verification as a **optimization resource allocation / stochastic process**



