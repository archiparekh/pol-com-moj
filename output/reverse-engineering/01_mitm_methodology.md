# Process
*note: revise this/pulled from thesis draft 1*

1. Download Moj APK
2. Decompile APK (using apktool d moj.apk)
3. Recompiled APK to make sure it was working fine
4. It was not recompiling properly because of some NullPointer errors in the xml file. I removed the two lines causing the errors (not sure what they corresponded to, probably small features)
5. Recompiled Moj APK (apktool b moj/dist or something like that)
6. Removed certificate pinning with apk-mitm 
7. Download recompiled app onto my phone (note: this has to be done when the phone is connected with the mitmproxy, otherwise i can't collect data)
8. Set up mitmproxy
9. explore the app and note down API calls

In order to identify videos of our topics of interest, I used the hashtag search service. After finding the endpoint, I crawled the data directly from the app by searching for a desired hashtag and scrolling (either manually or with an auto-scroll app). Infinite scrolling loads about 16 new videos on the phone screen. I set up MITMproxy to intercept these requests. After scrolling an arbitrary number of times or until results stopped loading, I downloaded the MITMproxy flow file. This recorded all the requests, request headers, and responses. Using a python script, I read all of the requests and compile the responses into a json file.
