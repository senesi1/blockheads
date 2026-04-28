
# The Big Picture: multi-level secure data management as a Merkle DAG

## Requirements
Provide a ledger system for the management of data movement through/inside a confined environment with multiple security levels.
At a high level, we propose modeling all data movement, access, and transformation as a Merkle Directed Acyclic Graph (DAG). A Merkle DAG is a generalization of a blockchain: whereas a blockchain enforces a linear sequence of blocks, a Merkle DAG allows a partial order of events, enabling parallel operations, branching, and merging while still preserving cryptographic integrity.

### Core idea: 


Every node (event or state) is hashed using a cryptographic hash function such as SHA-256

Each node’s hash depends on:
- its contents (data + metadata)
- the hashes of its parent nodes


Any modification to data or history changes the hash, breaking consistency


This yields a system where:

- Integrity is self-verifying
- Provenance is cryptographically bound
- Tampering is detectable and non-forgeable


Nodes = data states (files, objects, datasets) or events (reads, writes, transfers)
Edges = transformations or transfers
Labels = metadata (timestamp, classification level, actor, hash)


## What does this model buy us?
Our Merkle DAG is a Merkleized audit log.  The system acts as an append-only, tamper-evident audit log, where each new event is cryptographically linked to prior events via hashes. Unlike traditional logs, which rely on trusted storage, this structure ensures that:

- Any modification to past entries invalidates all downstream hashes
- The entire history is self-authenticating
- Audit logs cannot be altered without detection

Our Merkle DAG is a Cryptographic provenance graph. The DAG structure encodes data lineage explicitly:

- Every node points to its predecessors
- Full provenance is recoverable via graph traversal
- Relationships such as “derived from,” “copied from,” and “read by” are first-class: they are modeled as directed edges in the DAG.


This allows us to answer questions like:

- Where did this data originate?
- What transformations were applied?
- Who accessed it and when?


All answers are cryptographically verifiable, not just logged.  The answer to any of these questions is backed by a chain of hashes (and Merkle proofs) that a verifier can independently recompute.  Our Merkle DAG is a fundamentally append-only verifiable data structure.

- New events create new nodes
- Existing nodes are never modified
- History is immutable once committed


Verification reduces to checking:

- per-node Hash consistency (Merkle property)
- Structural and security validity of the DAG

This makes the system:

- Easy to audit
- Resistant to rollback attacks
- Suitable for distributed environments: removes the need for a single trusted authority to maintain consistent history, replacing it with locally verifiable cryptographic agreement on structure and history.



## Features
### Merges 
What is a merge, in our model? Unlike Git, where merges primarily reconcile repository histories, “merge” in our system has multiple meanings:

- Data merge: combining the contents of multiple data sources into a new object
- Conflict resolution: reconciling divergent edits to the same data
- Ledger merge (reconciliation): synchronizing independently evolving local DAGs into a globally consistent history

In practice, the most important notion for this system is ledger merge, which corresponds to committing locally generated history into a globally verifiable structure.

### Directory structure

We can also track evolving directory structure, as its own separate versioned object in a Merkle DAG.  At any moment, the directory structure is treated as a single content-addressed object.  Each directory is a node, including a hash of its own children (files and subdirectories).  The coupling between the file level DAG and the directory DAG is that events modify the directory state, and each modification produces a new root hash of the directory DAG.  This will give us 

- Point-in-time reconstruction: use directory root hash at a checkpoint.
- Structural provenance: we can prove that a file existed in a given directory at a given time, or that a file was moved from D1 to D2.  

If someone deletes a file, renames a directory, or alters structure, the root hash changes immediately. 

### Checkpoints and Merkle Proofs

#### Checkpoints
To make verification efficient and scalable, our design includes checkpoints, which are periodic cryptographic commitments to subsets of the DAG. Each checkpoint consists of the root hash of a Merkle tree constructed over the hashes of recently added DAG nodes, thereby committing to a set of events without explicitly storing them. Checkpoints are linked sequentially, forming a linear chain of commitments that anchors the evolving DAG into a compact and verifiable global history. These allow us to periodically “freeze” trust in a large, evolving history so it can be verified, audited, and agreed upon.  

A checkpoint:

- Commits to a set of events without storing them explicitly
- Provides a compact, tamper-evident summary of system activity
- Links to previous checkpoints, forming a linear chain of commitments

Importantly, checkpoints do not replace the DAG—they anchor it cryptographically, allowing the system to maintain a rich history while enabling efficient verification.

We need checkpoints:
- to anchor distributed activity into a global, agreed-upon state
- To bound the window of unverifiable activity
- To enable efficient verification without replaying all history


How do checkpoints work?

- Each node/event included in the checkpoint is hashed
- These hashes form the leaves of a Merkle tree
- The root hash becomes the checkpoint
- Checkpoints can be chained together for continuity


The nodes we include in a checkpoint would be determined in a principled, deterministic way.  For example, we could could include 

- all DAG nodes that have been added in a fixed time interval since the last checkpoint.  
- all leaf nodes, back to the last checkpoint, and execute the checkpoint at fixed time intervals. 
- all nodes within some scoped selection, satisfying certain criteria (e.g., in a certain container, or subject to a security constraint).

#### Merkle proofs 

A “Merkle proof from checkpoint root to a node” means:

Provide the hash path showing that a specific event (e.g., “file moved A→B”) is included in the checkpoint’s committed history.  We can prove:
- This exact event happened
- It was part of the committed history
- It was not altered



Summary: A checkpoint is a compact cryptographic commitment to a set of events (a subgraph of the DAG), typically implemented as the root of a Merkle tree over recent nodes ('recent' suitably defined).  We construct a separate Merkle tree over DAG node hashes to create a compact commitment to the DAG, enabling efficient inclusion proofs without traversing the full graph.  


We can also use Merkle proofs to verify the inclusion of an individual node within a checkpointed snapshot of the DAG. A Merkle proof consists of a minimal set of sibling hashes that allows a verifier to recompute the checkpoint root and confirm that a specific event was included in the set of DAG nodes committed at that checkpoint.

Checkpoints operate at the level of sets of events, committing to subsets of the DAG via a Merkle root, while Merkle proofs operate at the level of individual nodes, enabling efficient verification that a specific event is included in a committed snapshot without requiring traversal or reconstruction of the full DAG.

This separation enables scalable auditing: global system state is compactly summarized via checkpoints, while fine-grained verification of individual events can be performed in logarithmic time relative to the size of the committed set.

Checkpoints and per-node Merkle proofs solve different verification problems.  A checkpoint will tell us “what set of events is committed."  A Merkle proof will tell us that “this specific event is part of that committed set.”

## The Big DAG

We have one big underlying event-driven Merkle DAG, and three committed substructures derived from it: 

1) File-content DAG (data lineage layer).  Captures file contents (states), transformations (edit, copy), and access events (read).  
2) Directory-state DAG (structure layer).  Captures where files live at a given time; restructures; directory composition.  Nodes are directory snapshots, edges are structural transitions.
3) Checkpoint chain.  Captures periodic cryptographic commitments, Merkle roots over subsets of the DAG(s), global synchronization points. Nodes are checkpoint regords, and edges give us a linear time-ordered hash chain. This is a blockchain-like sequence of commitments.

Summary: The file DAG tracks events, the directory DAG tracks structure, and the checkpoint DAG (blockchain) tracks committed truth.

## Security verification
We model classification levels (e.g., Unclassified ≤ Secret ≤ Top Secret) as a partially ordered set (poset) from lattice theory.
Each node is assigned a classification label:
L: Nodes -> Security Levels

We enforce the constraint: for any edge u -> v, we enforce/require L(u) <= L(v)


So data can flow upward in classification, and cannot flow downward without explicit transformation.

### Implimentation:  

Security is enforced at node creation time.  Recall that a node is constructed, then validated, then hashed, then committed.  The security rule (L(u) < L(v)) is enforced before the hash is finalized. 

Each node includes its classification explicitly (as metadata).  The security label is part of the hashed content.  It is cryptographically bound, so one cannot silently change the classification later.  


This ensures that there is no unauthorized data leakage, and all flows are policy-compliant.  Any security violations are detectable via graph validation. 

The system gives us two-layer enforcement: we have a local rule (before hashing), enforcing monotone constraint at node creation time, and global verification after the fact, whe we recompute the DAG and verify that no invalid edges exist.

### Summary:
 The security problem is reduced to verifying that the DAG respects a monotone labeling over a partially ordered set of security levels.  Security becomes a graph invariant rather than an external enforcement mechanism.

## Logarithmic complexity

One verification task is to prove inclusion of a node within a set of nodes committed to some checkpoint.  

To prove inclusion without Merkle trees:

send all N events (N = total number of nodes).  The verifier recomputes everything, at cost = O(N).

Merkle proof/verification:

We send only one hash per tree level.  If there are N leaves,  proof size is approx. log⁡2(N). 

Why logarithmic?.  Each level of the tree halves the problem.  Tree height = log⁡2(N).  Verification walks a single path from leaf to root. 

Summary: verification cost grows with the height of the tree (log N), not the number of events (N), making it scalable.





## Computational costs, storage costs, and tradeoffs
###Computational costs

Hashing cost: proportional to data size

Merkle tree construction: O(N) per checkpoint

Verification: O(log⁡N) per proof


### Computational Cost Tradeoff:


Frequent checkpoints: higher compute overhead

Infrequent checkpoints: larger verification windows



### Storage costs:

Each node stores metadata + hashes
Data stored once via content-addressing (deduplication benefit)
Checkpoints add minimal overhead (single hash + metadata)







