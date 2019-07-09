# Advertisement platform 
*July 2017* 

In this project, I designed and developed a web platform for advertisement in Django (Python). This project focused entirely on the platform design, back-end development and the minimum viable front-end (functionality was heavily prioritized over beauty).

Django is used for the backend. Some additionnal libraries are used, such as *PIL* for the image processing or *allauth* to handle logins with social media.

The frontend is created using HTML/CSS/JavaScript, and jQuery for the image manipulation.


You can find all the code in the ``src/`` folder

**Table of Contents:**

[Demo](#Demo) - Short video showing of the platform<br>
[Project Idea](#Project-idea) - How does it work<br>
[Matching requirements](#Matching-requirements) - Some interesting constraints that the platform tries to solve<br>
[Architecture](#Architecture) - A brief overview of the platform architecture

## Demo
Here is a 1 minute demo of the final project (everything you see is working in the backend):

<p>
    <a href="https://youtu.be/-_tzhh94bHg">
        <img src="github_content/youtube_thumbnails.png" alt="project demo thumnails on youtube" width="400">
    </a>
    <em>Clicking on the video will take you to youtube</em>
</p>

## Project Idea
The main idea is to have "social media celebrities" advertise on behalf of companies.

These web celebrities will select products they like, from companies they like and advertise the product on their social media accounts. In contrary to ads you can find on Google or Facebook that are separated from the content produced by users, the ad will be directly integrated to a picture the star creates.

Following is a summary of the steps that will be done on the platform:
1. Connect a company to a web celebrity.<br/>
<img src="github_content/step1.png" alt="step 1" width="400">

2. The web celebrity creates an image endorsing the company.<br/>
<img src="github_content/step2.png" alt="step 2" width="700">

3. The web celebrity posts the image on social media.<br/>
<img src="github_content/step3.png" alt="step 3" width="570">

4. The company renumerates the web celebrity.<br/>
<img src="github_content/step4.png" alt="step 4" width="250">


## Matching requirements
The main problem that needs to be solved, is how to match the workers (web celebrities) with the companies. Looking at the various player goals, we have that:

1. The companies want to:
    1. Maximize their positive visibility.
    2. Minimize the money spent.
2. The workers want to:
    1. Maximize the money they earn.
    2. Minimize (on their audience) the negative looks they could get from making ads.
    3. Minimize the work they do.
3. The platform wants to:
    1. Maximize the amount and number of transactions between the companies and workers.
    

Most of the goals align well, however two goals can be deal breakers:
1. Companies will want to have control over who is promoting their brand.
2. Web celebrities also want to have some control over which companies they promote: for example a sportsman may not want to promote unhealthy food.

This leads us to our architecture that tries maximize the number of possible transactions knowing these limitations.

## Architecture
- The companies will be able to select which web celebrities they would accept. For each celebrity (or group of celebrity), they will propose a price that they are willing to offer to them if the celebrity posts a sponsored picture.
- A celebrity will see all the companies that have made a propostion to him, ordered by how both the companies and the worker fit together. He will be able to accept a proposition.
- Once a celebrity has accepted a proposition, he will need to prepare a picture to post, that he will build with the platform itself.
- The picture will then be sent to the company for validation.
- Back and forth can happen, but once validated, the picture will be posted on social media.
- In the long run, different metrics would be compiled (number of likes on the picture, effectiveness of the collaboration, etc.) and will allow the system to improve the matching proposition between companies and celebrities

Below, you can find the detailed architecture of the system as it was implemented here:

<img src="github_content/uml.png" alt="uml diagram of the architecture" width="80%">