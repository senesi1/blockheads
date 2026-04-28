# Why checkpoints in a Merkle DAG?

The key idea: Merkle integrity ≠ agreement on which history matters.
Checkpoints solve consensus, anchoring, and recovery problems—not just integrity.

Checkpoints give us official history (up to the root hash of the checkpoint).  
Only descendants of the checkpoint are valid, going forward.  
Instead of verifying the entire DAG, we can verify checkpoint signature.  Or to verify a post-checkpoint node, we can verify the path from the last checkpoint to the given node.  The complexity of verification drops from O(N) to O(log N), or a small traversal. 


Protection against replay: 
If someone presents an older DAG, and its root is different from 
