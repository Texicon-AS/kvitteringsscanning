This repository contains the files used in the foodmanager repository for the receipt scanning functionality. It is not meant to be runnable, only to get insight into how the solution works.

Parts:
1. Rust code from the grpc server containing the main business logic, that contains the scanning functionality. 
2. Typescript file containing the REST endpoints (as image uploads dont work well with grpc) for the image upload to the different AI services. 
3. Centric´s receipt text to ingredient solution.
