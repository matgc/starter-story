---
video_id: "gpn1jEoWT4A"
title: "How I Built It: $15K/month Mobile App"
published: 2025-06-21
duration_seconds: 806
source: https://www.youtube.com/watch?v=gpn1jEoWT4A
transcript_source: YouTube automatic captions (en-orig)
---

# How I Built It: $15K/month Mobile App

[Watch on YouTube](https://www.youtube.com/watch?v=gpn1jEoWT4A)

## Marketing strategy summary

- Target consumers who want a visually appealing, simple habit tracker on iOS and Android; Habit Kit reduces friction with basic tracking, grid-based progress, local-only data, and no sign-in.
- Use app-store search as the main scalable acquisition channel: Habit Kit reached the top five for important terms such as "habit tracker," which drove organic traffic without a large marketing budget.
- Build in public for early reach and credibility by sharing authentic progress, wins, and failures across X, LinkedIn, BlueSky, and Threads; Sebastian said this led to podcast appearances, video features, and relationships with other app developers.
- Optimize store metadata around one high-intent keyword: place it at the start of the app name, refine the subtitle, keyword fields, and screenshots, and use tools such as Astro and Appfigures for keyword and performance research.
- Ask for ratings at the user's first success moment: Habit Kit shows the native review prompt immediately after a user checks off a first habit, helping it accumulate more than 2,000 reviews and ratings across roughly 300,000 downloads.
- Validate through founder-problem fit and visible response: Sebastian builds products that solve his own problems, acts as the first customer, and accelerated Habit Kit's launch after early screenshots received a positive response.
- Monetization evidence: monthly recurring revenue rose from about $3,000 at the end of 2023 to more than $15,000 at the end of 2024; operating costs were roughly $200-$300 per month plus RevenueCat's 1% fee. Caveat: the claim that a $100-per-month Apple Search Ads campaign may improve organic ranking was presented as Sebastian's hope, not a confirmed result, and the strategy depends heavily on app-store rankings.

### Reusable playbook

1. Choose a recurring problem you personally understand and define the smallest mobile workflow that solves it.
2. Build a clean cross-platform MVP around that core action, then share screenshots and honest progress on several founder and professional networks before launch.
3. Use keyword data to select one high-intent app-store query; put it first in the app name and align the subtitle, keyword fields, and screenshots with it.
4. Trigger the native rating prompt immediately after the user's first completed action, when the product has just delivered value.
5. Run a small search-ad test around the target query, but treat any ranking effect as a hypothesis and track paid and organic performance separately.
6. Keep improving the product and store listing while monitoring keyword rank, downloads, ratings, recurring revenue, and platform fees.

## Transcript

> This transcript was derived from YouTube's English automatic captions. Timestamps mark the start of each caption group. Names and technical terms may contain captioning errors.

[00:00:00] I turned a simple habit tracker into a 15K MR business. Sebastian Ro always wanted to build his own apps. So he decided to quit his job and give himself 12 months to figure it out. No plan, no idea, just a dream to build. I quit my job with no idea, just 12 months of runway. But 6 months in, he had less than a dozen downloads on his app and he was faced with a decision. He changed up his strategy and then found an idea that changed everything. And then in under two years, he went from just building side projects that made him a few hundred bucks to a full-time solo

[00:00:34] developer making $15,000 a month on the app store. The secret to reaching top 10 in the app stores is In this video, I bring Sebastian onto the channel to break down what happened after he quit his job and it's not what you'd expect. We'll also go over his failed ideas and why they didn't work. And he'll share the secret to why his app has been downloaded over 300,000 times. This is the playbook to building successful apps. I'm Pat Walls and this is Starter Welcome Sebastian to Starter Story.

[00:01:07] Thanks for coming on. So tell me, what's your story? Hi, thank you for having me. My name is Sebastian. I am 32 years old. I'm living in Germany and yeah, I'm the creator of Habit Kit. It's a visually appealing and very simple habit tracking mobile app that helps users build and maintain their daily habits. I launched Habit Kit in 2022 after I quit my corporate programming job to uh finally become a full-time indie app developer.

[00:01:35] Since then, my app has grown significantly, reaching $15,000 in monthly recurring revenue through a combination of building in public and effective app store optimization. Beautiful. Okay. Well, let's dive a little bit more into this business and some of the numbers behind it. I have roughly 300,000 downloads on the App Store and Google Play combined and over 2,000 reviews and ratings. I'm ranking for various important keywords in the habit tracking space. The most important one is habit tracker in the top five in multiple countries for that. I love that. Let's go right into uh development

[00:02:15] of the app. I know that you have a software development background. Tell me about how you built this app. Uh yeah, sure. I had the idea for habit kits uh in summer of 2022. I immediately started building the app and I used flatter for this. That's a crossplatform framework that allows you to deploy your apps to iOS and Android with a single codebase. When I started, I focused on the core functionality. It was a tilebased grid chart for the users habits with a clean and super simple interface. And the MVP features just included the basic habit tracking and the visualization of the

[00:02:55] progress. And I built it with privacy in mind. All data is stored locally on the device. There's no sign in required, no authentication. The users have complete control over their data. I also decided to share the development progress on my social media. And after posting the first screenshots and seeing a positive reception, I knew that I should really hurry up and bring the app to the app store and uh make it quick. I kept it really simple and clean and just banged it out in 2 months. So, let's take a step back and I want to learn a little bit more about your past, your

[00:03:34] background. What were you doing before this and how did that lead to coming up with the idea for Habit Kit? Yeah. So, um, my background is pretty straightforward. After school, I studied computer science at a university here in Germany for roughly 6 years and did my master's thesis and after that I started a regular programming job at a middlesized company here in Germany as well. I learned a lot there. But uh after 3 years of being stuck in the same project there, I became a little bit restless and wanted to be a little bit creative and work on my own projects. So

[00:04:14] after 3 years of the same project at my regular job, I decided it was time to quit my job and focus on indie development for at least 12 months. The first 6 months were really challenging. um I didn't had a lot of revenue so I kept in touch with the people at my old job and after the my my 12 month deadline was over I decided to go back to my old job and continue doing my app business on the side. I felt like a failure and like a success because I had at least some revenue. It wasn't really high, but I think it's already a huge success if you have a side business with

[00:04:57] $1,000 revenue. At the end of 2023, I finally reached $3,000 in monthly recurring revenue. At the end of 2024, I achieved over $15,000 in MR. I quit my job the second time uh at the start of 2024 and I'm finally able to to have complete control over my time and work on whatever I want. All right, before we dive into how Sebastian built his app to over 300,000 downloads, let's talk about something that trips up way too many founders. Not setting up your business in the right way. You spend months building, marketing, growing, but if you're not legally protected or even

[00:05:42] registered properly, one mistake can wreck everything. That's why we're excited to partner with Zen Business. Zen Business empowers entrepreneurs from all walks of life to confidently start, protect, and grow their business. With their worry-free platform, award-winning support, and AI powered tools, anyone can achieve success on their own terms. Zen Business helps you form your LLC in minutes so your business is real, protected, and ready to grow. Over 800,000 founders have use Zen Business to launch and grow, and it's priced to fit any budget. You can get started for

[00:06:17] $0 plus state fees in about 5 minutes. So, if you're serious about what you're building, this is the first step. Click the first link in the description to launch your LLC today at $0 plus state fees and get started today. Thanks to Zen Business for sponsoring. Now, let's get back to Sebastian's story. I want to get a little bit more tactical. How did you actually grow this business and what marketing channels did you use for Habitat? In the beginning, building in public was huge for me. I shared my journey and development process across multiple platforms like X, LinkedIn,

[00:06:52] Blue Sky, and Threads. I tried to create authentic content, share about my wins, failures, successes and so on that led to unexpected opportunities, being guest on podcasts, being featured on videos or having good connections to other app developers. So that was a huge uh part of my success in the beginning. Another important aspect are search ads. Um I just I won a super simple and lowbudget Apple search ads campaign. Um, I only spent $100 per month on it. I just used this as a potential ranking boost strategy because I have the hope that Apple favors developers who also run ads

[00:07:35] on their platform. And after that, uh, the biggest thing probably was app store optimization. App Store optimization is basically editing your app store meta data like keywords, app name, or subtitle or even the screenshots in the way that you're more likely to rank in the top spots when people search for certain keywords. I'm focusing on the habit tracker keyword and that's why I put it right at the start of my app name. Another important aspect of ASO is um gathering user reviews for your app.

[00:08:11] I um instantly show the native review dialogue. So it says, "Do you like habit kits? Please review it on the app store or something like that right after the first habit uh was checked off for a user." So that that's their first success moment. and I asked them right at this situation and most people just gave it five stars and you gain a lot of reviews and ratings. Yeah. So, gathering uh reviews is pretty important.

[00:08:39] Beautiful. Let's talk about ideas. You've launched a few things on the app store. Some of them were flops, some of them are hugely successful. Tell me about your process for finding ideas and validating them. In terms of finding good ideas, my recommendation is to just start building anything. It doesn't matter what exactly. Once you get into the groove and start building something, you will naturally get a ton of other great cool ideas for later projects. In terms of validation, I just build apps that solve my own problems. Um, I will always be my first customer and so I

[00:09:13] always know exactly what's needed in the product, what are the requirements and what works and what not. Cool. I love that. So, you have an app, it makes $15,000 a month. walk me through the different technologies and stack that you use to actually build this app. As in terms of development tools, I use Flutter. That's a crossplatform framework for for building mobile apps uh for iOS and Android with a single codebase. I use uh cursor as my AI powered IDE. Um, I love the autocomp completions that the AI provides and I love to chat about different problems with it. To do my keyword research and

[00:09:53] ASO optimizations, I used a tool called Astro. It yeah, it allows you to search for keywords on the app store and see their popularity and difficulty. For app analytics and marketing and also a little bit of keyword research, I use app figures. And in terms of uh handling subscriptions and purchases in my apps, I use a service called Revenue Cat. Yeah. And for personal habit tracking, I use Habit Kit, of course. I also use some other tools like Waycast, which is a collection of productivity tools for your Mac and Chat with AI, one password.

[00:10:32] These are some very important tools in my tool chain. Okay, cool. On a similar note, let's talk about costs. Uh I know you're a solarreneur. You're running this yourself. You built everything out. You don't have any employees. How much does it actually cost in total to run an app like this? Yeah. So, um my expenses are super low. Um my biggest expense is revenue kit right now because uh they take um 1% of my revenue. So, depending on the month of the year, that can be a lot, but it's totally worth it. And yeah, the rest can be added up to roughly $200 or $300 per month. So it's

[00:11:12] really low. Nice. Wow. Okay, cool. So your app makes $15,000 a month. You've kind of gone through the process of building something successful. What is something that you learned in the process that you didn't expect? Yeah, I was super surprised um that I was able to to compete in the App Store and Google Play with bigger companies or people that are super long on the app store. I reached top five in super important keywords uh which drives a ton of organic traffic to my apps. And yeah, if you manage to secure a good ranking on the app store, you don't need a big

[00:11:48] marketing budget and you can compete with with bigger brands. Nice. Cool. Well, the last question that we ask all founders that come on Starter Story, if you could go back in time and give advice to Sebastian right when he quit his job, what advice would you give? I would say save money for Sabbatical to focus on development of your app business like I did. I saved some money and I just quit my job and set myself a deadline for 12 months to do something that works. Yeah. because I couldn't find motivation to code on my own apps after I programmed for 8 hours on my

[00:12:23] regular job. So quitting my job was actually the only chance to to get this started. And yeah, this ultimately helped me to focus on my stuff and lay the important foundation and ultimately for my dream business. Yeah, I love that. You know, a lot of people think what's going to happen if I quit my job. Uh, but at the end of the day, you can just go back and get another job. And that's exactly what happened to you. And I just love this story. Thank you for coming on, Sebastian, and sharing everything about your business, going deep, sharing a bunch of things that you

[00:12:53] didn't have to. You're awesome. Thanks for coming on, Starter Story. Thank you for having me. All right. I love Sebastian's story. It shows you the power of building on platforms. We talked all about ASO, which I think is super cool. So, hopefully that was helpful. If you want to build something similar to Sebastian, check out Starter Story Build. is our platform for building a real app going from an idea to a launched app in 12 days. I'll put that link in the description. Thank you guys for watching. I'll leave you with one question. What's your story? Peace.

## Links mentioned in the description

- [Complete your LLC filing today](https://go.starterstory.com/zenbusiness) - [local notes](../../links/channel/complete-your-llc-filing-today.md)
- [Learn how to build mobile apps](http://build.starterstory.com/build/ios-bootcamp?utm_source=youtube&utm_campaign=sebastian) - [local notes](../../links/channel/learn-how-to-build-mobile-apps.md)
- [Sebastian Röhl (@SebastianRoehl) on X](https://x.com/SebastianRoehl) - [local notes](../../links/video/sebastian-rohl-sebastianroehl-on-x.md)
- [Starter Story Build on YouTube](https://www.youtube.com/@StarterStoryBuild) - [local notes](../../links/channel/starter-story-build-on-youtube.md)
- [Starter Story Jobs](https://www.starterstory.com/jobs) - [local notes](../../links/channel/starter-story-jobs.md)
