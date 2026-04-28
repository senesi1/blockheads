# Checkpoints: purpose, structure, design, implimentation

## Why checkpoints in a Merkle DAG?

The key idea: Merkle integrity ≠ agreement on which history matters.
Checkpoints solve consensus, anchoring, and recovery problems—not just integrity.

Checkpoints give us official history (up to the root hash of the checkpoint).  
Only descendants of the checkpoint are valid, going forward.  
Instead of verifying the entire DAG, we can verify checkpoint signature.  Or to verify a post-checkpoint node, we can verify the path from the last checkpoint to the given node.  The complexity of verification drops from O(N) to O(log N), or a small traversal. 


### Protection against replay: 
If someone presents an older DAG, and its root is different from the latest checkpoint, then it is immediately rejected.  

### Boundary enforcement: 
When moving data across security levels, we can choose to only allow data derived from approved checkpoints.  This provides auditable provenance boundaries.  


## Checkpoint policy 
Checkpointing is a policy decision, not just a data structure feature. If we pick the span or timing poorly, we either lose efficiency or weaken guarantees.  The fundamental tradeoff: 

### The tradeoffs 
Frequent checkpoints -> less room for ambiguity or replay
Short spans -> tighter control over what is 'agreed'
Longer spans -> more freedom to build branches
Fewer checkpoints -> less coordination required

A 'checkpoint span' is not just 'how many nodes'.  It is a commitment to a 'cut' through the DAG.  This cut could be defined by time, topology, security level, or event boundares (e.g., "after a data transfer completes").  

### Effective patterns for checkpoint policy: 
#### Boundary-based: checkpoint when data crosses security level, organizational boundaries, trust domains 
#### Epoch-based: Group DAG updates into 'epochs': e.g., every N operations, T seconds, or every batch job 
#### Event-driven: Checkpoint when:V dataset is finalized, model is trained, transaction batch closes. 


