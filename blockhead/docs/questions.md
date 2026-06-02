"Data lineage is fully recoverable"? Even if someone uses a provenance-disabled tool? Perhaps this means "if everyone uses provenance-enabled tools, then no one can get away with editting the logs"?

How is "policy compliance a structural invariant of the system"?

What's the proposed algorithm? Add to the blockdag on each operation, both reads and writes. How can I confirm I'm seeing the whole DAG?

File exists on remote system
Checkout: Download a local copy
Checkin: Upload changes
Checkin: Affirm I'm done with the file and have deleted it. (Upload unchanged)

How can I help?

James: 20 hr/week; C, systems, networking, 30 years implementing Seth's ideas, some Python, good at Perl, Bash
Prasad: 20 hr/week; Maths :)

Prasad likes spending lots of time on Teams (maybe daily)
REST side vs. Compute side. Python

Django
FastAPI
CherryPy

Where's the build env?

According to Ray:
Document reasonable assumptions about comms between enclaves.
We should be gunning to produce something small that demonstrates exactly what a check-in system looks like, and how it might scale. If the POC is small, we might have time to see what a "hooks-based" system looks/performs like.
I had hand-waived a preliminary environment with three connected VMs or containers (A <-> B <-> C) to model separate enclaves. Then we could simulate a file entering from A and leaving C and request a report for that file.
There might be a central filesystem (outlook, palantir foundary, various other mounted file systems)
If the IS owner (IS=SAV, for example) is given a list of files that showed up in a place that maybe they shouldn't have, the owner can easily produce a report to support an investigation that details where that file has been in their system, and who was responsible for moving the file.

