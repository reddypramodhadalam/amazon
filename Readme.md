
Clone and import the project as existing Maven project in any Java IDE.
you can run the program using any IDE like Eclipse or IntelliJ or from Jenkins but Ensure Maven plugin is available. 
Run the program by using the command - clean install exec:java

Introduction
Appium TestNG Framework 

This is a page object model framework. Below are the features that are incorporated and their status.

1) Page Modeling Example
2) Red data from yaml file
3) Appium Repository contains all possible permutation and  combination of actions,events and etc that can be performed in a web page
4) TestNG Listener Implementation
5) TestNG Reporter Implementataion 
6) HTML End Report Generation- Sample is added. Required to be modified as per the project/requirement

What happens when a build is triggered
 Step 1. Build is triggered through Maven by using the command- clean install exec:java
 Step 2. It triggers the testNG.xml. testNG.xml file have 2 script mapped
 Step 3. Prior to script start below methods runs
            i) TestNG BeforeTest (This method will run before every script. In our case 2 times it will run once before script1 and again before script2) – It starts a browser. Before browser start if any proxy is configured then it is set and all the temporary files in the system is cleaned. So that browser can have a clean and fresh session.
Step 4. Then the 1st script is executed. 
        After Execution of the script below method executes
        i)  TestNG AfterTest Method- It closes the browser instance 
