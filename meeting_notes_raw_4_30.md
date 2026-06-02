

April 30, 2026

WE need to have a proposal for the various different ways we could begin to design this.  Talk to Ray about which way to go.  

Levels of checkout counter: two different extremes.  Full counter vs. kiosk

Git-like approach to prototype something fast!  Checkout counter offers more features.  

For the mini-git: do we really just need mini-git + security?

Git, as a system, provides us with hooks all over the place.  We're going to use git, but require to use it in the CVS model where there is a central repo, and everyone is a node on a spoke.  And then we could, initially, have pre-commit checks: A thing that we set up, a program, run this thing, I'll hand you the...
When the data arrives on the other side, where git is living, we push our changes into that remote git repo.  That repo can be set up so there's a hook that runs before the official 'push'.  (Does git have a pre-fetch hook?) 

The problem with using Git: We're including a file system structure.  Ray might not want this initially.  

POC: 

RCS vs. CVS

Check-in verifications 
Check-out verifications

RCS: 
- (In RCS, with each check-in, it stores just the diffs.  So it will build the file diff-by-diff.  OTOH, Git stores the entire blob and puts it into the repo.

What are the events we would track in this case? 
Check-out, 
Check-in.

)
- access rights need to be verified.  
- If there's already a version, we have to merge the changes to local.  

Merkle DAGs only exist locally. 



CVS: 

need to handle merge conflicts.  There are programs that will do this for us; places conflict markers where it can. 
Merkle DAG exists globally.  



Does person have authorization?  
Has the person attempted to lower the security status on the file prior to check it? 
Does the person have the authority to do this?  

AT some point, it might be interesting to have functionality where certain paragraphs are security-coded.  

James: I hope we do not have to use Async io!!!!


... and what steps would be necessary to develop it...????
Maybe he just wants to know what operations 
check in 
check out 
+ Verification 
Checkpointing/tagging
(In git, every sha1 sum is the identifier for a node in the merkle tree.  A tag is literally nothign more than a symbolic name that maps to a sha1 sum.  In the original version of Git, tags were literally file names where the file name was the tag name, and the file contenst were the ascii version of the sha1 sum.  and that was it.  The piont is, by knowinbg the sha1 sum, we can find it in the tree. and we check out that version of the file and it's fixed.  In git, when we check out a tag, we are in a headless state. We could create a branch here, this is legal and sometimes desired.  But we  cannot modify the thing that that tag points to, because igt's committed.)
w/ collision detection

What version of sha should we use?  We should probably use the FIPS-approbed version; presumably we have a govt customer.  If we mention anything that's cryptographic and not fips, we will get pushback.  

Don't forget checkout counter / kiosk spectrum.  Continuous vs. discrete spectrum.  We assume Ray will probably go for the CVS.  

Do we want to write from scratch? Modify Git?  Modify CVS?  (Written in C)




