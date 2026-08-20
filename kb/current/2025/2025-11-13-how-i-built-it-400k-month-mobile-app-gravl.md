---
video_id: "2dfMUtHlQik"
title: "How I Built It: $400K/Month Mobile App (Gravl)"
published: 2025-11-13
duration_seconds: 934
source: https://www.youtube.com/watch?v=2dfMUtHlQik
transcript_source: YouTube automatic captions (en-orig)
---

# How I Built It: $400K/Month Mobile App (Gravl)

[Watch on YouTube](https://www.youtube.com/watch?v=2dfMUtHlQik)

## Marketing strategy summary

- Gravl targets strength-training and gym users who want workouts tailored to their equipment, schedule, goals, experience, and recovery; Julian pursued the idea after finding a leading competitor's generated workouts weird and sometimes dangerous.
- The first validation channel was Reddit: a technical build thread earned more than 300,000 impressions and brought the first couple thousand users, whose bug reports and feature requests convinced the team to add subscriptions and build a serious business.
- Paid acquisition became the main growth engine. The team began below $50 per day, translated the app into Spanish, and bought cheaper traffic in South America before scaling across Meta, TikTok, Google, and Apple Search Ads.
- Their creative system favors high-volume UGC: hire creators for as little as $50, use AI and CapCut to make more variants, inspect competitors in Meta's public Ads Library, and adapt proven concepts rather than inventing every ad from scratch.
- They recommend validating willingness to pay before buying ads, starting with low spend, and testing lower-cost geographies; the hard part is producing enough creative volume to find winners.
- Gravl reported more than 70,000 subscribers and over $440,000 in the latest month. Paid media consumed about one-third of revenue, Apple took 15%, salaries were roughly $50,000-$80,000, and infrastructure and attribution tools were about $1,000 each per month.
- Caveats: the exact payback period, retention, pricing, and campaign-level unit economics were not disclosed, and the performance figures are founder-reported.

### Reusable playbook

1. Start with a problem you know deeply, then study a proven product and define a meaningful improvement for a clear user group.
2. Launch a focused MVP in a relevant community and use real usage, bug reports, feature requests, and paid conversions to validate demand.
3. Add monetization before scaling acquisition so ad tests measure willingness to pay, not just installs.
4. Begin with small ad budgets and test cheaper languages or regions where the team has a real localization advantage.
5. Produce UGC in volume, study long-running competitor ads, and iterate on proven concepts with creators, AI tools, and simple editing software.
6. Scale only while subscription revenue covers media, platform fees, creative production, support, salaries, and infrastructure.

## Transcript

> This transcript was derived from YouTube's English automatic captions. Timestamps mark the start of each caption group. Names and technical terms may contain captioning errors.

[00:00:00] Last month, we made over $440K. Meet Julian, a developer from Argentina who built an app that makes over $400,000 a month. But it didn't start that way. Before the success, Julian was a dude at the gym who discovered a different app that he thought was pretty cool. However, instead of just using it himself, he thought, "What if I built something better?" And that's exactly what he did. He built an MVP, posted about it on Reddit, and the rest is history. I posted this thread on how I build. We got our first couple of thousand users. I can't really remember, but it was a lot. That was the biggest

[00:00:37] high probably I've ever had. I brought Julian onto the channel to break down this story and how he actually built an app used by hundreds of thousands of people. In this episode, we'll dive into the original app he cloned in just two months. The simple Reddit strategy that got him his first users and product market fit and the marketing playbook that scaled his app to over $400,000 a month. Let's dive in. I'm Pat Walls and this is Starter Story.

[00:01:06] All right, Julian, welcome to the channel. Tell me about who you are, what you built, and what's your story. Hey Pat, I'm Julian. I'm one of the co-founders and developer of Gravel, an AI fitness app that provide smart workouts for the gym. We launched around 2 years ago and now we have over 70,000 subscribers. Last month we made over Okay, over 400K with an app is insane.

[00:01:33] We're going to get all into that, but before we do, I want to understand a little bit more about your background. How do you even get into building an I grew up in Argentina. My dad used to own a fitness center. I pretty much spent all my time outside of school just playing sports and at the gym. I then got into software engineering and uh moved to Australia. And yeah, here I worked from small startups to big tech companies like Atlassian, a few TV channels, even an investment fund. And around co my best friend and also our partner came up with the idea of starting a company. It was like a at

[00:02:11] start a influencer marketing platform for mobile games. That's how we started. Fast forward a couple years, we ended up being some sort of a marketing agency which was something that I didn't sign up for. Neither did the guys. But the good thing is that we learned a lot about uh user acquisition and marketing, but also what the numbers were. So, in terms of revenue and after seeing some of those numbers, we obviously thought apps make a lot of money and especially fitness apps. So, we kind of used our background to decide that we wanted to start our own app.

[00:02:43] You had this business. You started with partners. It wasn't really what you wanted to build. Maybe it wasn't fully scalable. How does that turn into building an app that now makes over $400,000 a month? The business wasn't doing great. And because we transitioned into this kind of agency format, I had all this like energy for developing something that wasn't being used. So, I started with a more like a workout tracker kind of app.

[00:03:07] So apps like heavy, strong, that kind of thing. But as I was building it, I noticed that okay, I'm not adding any value. It just felt like copy of what they were doing. And then it was one of my mates. He showed me Fitbot. And Fitbot is one of the biggest workout app. And when he showed me the app, I was like, "Oh, like this is amazing." Cuz it kind of provided you with workouts on the spot and you didn't really have to do anything else. But then I started using it, doing some research. I noticed that the workouts were weird and even a bit dangerous sometimes. And like the more I used it,

[00:03:43] I was like, "Wow, okay, these workouts are actually bad." That's what triggered me. And then I was like, "Okay, this is it. We need to build FitBot UI UX with an actual proper workout engine." That's kind of when we went all in on building Can you tell me a little bit more about how you built it and how long it took? Initial MVP took around two to three months maybe. We can split the MVP into two parts. First part being pre FitBot and then after Fitbot. The first part of the MVP was more of the tracker. Then we transition into the Fitbot stuff and that's when things got trickier. There's

[00:04:23] a lot of business logic around building custom workouts for people. There's just a lot of different settings and combinations. Things like equipment, things like your weekly goal, how often do you go to the gym, are you consistent, uh your gender, your weight, your age. There's just so many things to consider. That was the definitely the the most challenging part.

[00:04:45] Tell me about how you launched this, how you got your first customer. What did you do to get this app off the ground and get into people's hands? I'm a massive supporter of of Reddit as a distribution channel. I posted this thread on how I built Gravel. Back in the day, it was called Games AI and I shared kind of the technical specs around it. It got over a couple hundred likes within the first couple hours and over 300,000 impressions. Yeah, we got our first couple thousand us. I can't really remember, but it was a lot. We found out that because they're developers and they like tech and some

[00:05:20] of them might like going to the gym, but they feel like it's a bit intimidating. I feel like a lot of them were actually using the app. And then we started getting feedback about like bugs and feature requests and were like, "Okay, we were on to something." And that was the final push that we needed cuz at this point the app was was free. And we're like, "Okay, now we need to build like a serious business out of this and and try to start running some ads for Okay, let's talk about something that is changing the game for builders right now. AI. Now, I know we talk about AI

[00:05:51] apps a lot on this channel, but I still get this question every day from builders. Where do I even start? That's where HubSpot for Startup's AI adoption playbook comes in handy. It's a free guide with a three-step framework on how to use AI inside your business. Inside, you'll learn how to spot AI opportunities in your workflow, implement AI without hiring expensive consultants, and see the exact playbooks companies are using to get real results.

[00:06:18] What's even cooler is it's sourced from executives at HubSpot, Enthropic, and Replet, some of the biggest AI companies in the world right now. My favorite part is inside the case studies where you will see exactly how one company booked 11,000 meetings and another resolved customer issues 39% faster using this framework. These are real numbers from real businesses. So, if you're ready to get ahead in the AI race, download HubSpot for Startup's free AI adoption playbook at the first link in the description below. Thank you to HubSpot for sponsoring this video. Let's get

[00:06:51] back into it. I'm sure that probably isn't what got you to over $400,000 a month. So, what has been the actual distribution strategy or the secret sauce behind Gravel on how it grew to over $4 million a year? For us, the bigger distribution was paid ads. We started running ads as soon as we obviously added the subscription model. I still remember like running our first app. We got a subscription within the first 10 minutes of like activating the ads. Yeah, that was the [music] biggest high probably I've ever had. And after that, we translated the app to Spanish. We started running ads on South

[00:07:30] America. And we were spending less than 50 bucks a day on ads. And that's what worked for us from the start up until this day. The next question I have for you that I'm curious about is you've built this app. It's huge. It's doing over $400,000 a month. What would be your top learnings or top tips for anyone building apps in 2025, specifically consumer apps or even uh fitness specific?

[00:07:53] The tip number one for sure will be to validate before spending money on ads. And when I say validate, it's not just that the product work, but also that people are willing to pay for it. That's also something very important. Tip number two would be and this is where we kind of got lucky because well I'm Spanish speaking and Matias as well so we're like it makes sense for us to translate it into Spanish and then potentially running ads that are cheaper in in South America the US even though we all want to end up there and running ads there is expensive there's a lot of

[00:08:27] competition tip three is start small you can pay influencers or content creator as low as 50 bucks for some piece of content. You can use AI tools to create videos. You can use Capkart to edit your own videos and you can get some pretty good results with that. It's not as hard as you think to create an ad. The hard thing is is creating the volume. And tip four, like I said, UGC is king. You'll see that most of the ads that work out there are UGC [music] content. You'll seeing a lot of AI videos and that's cost of producing them is cheap and they're easy to test. Last

[00:09:02] thing would be copy. copy and copy. Good thing about Meta Ads library is that it's all public. You can go into any of your competitions dashboard and see, you know, which ads are working for them, where they putting more money and yeah, there's no secret source there. Just copy what works for them and start like that. It'll probably work for you. I would definitely start there.

[00:09:27] Okay, cool. Well, those tips were amazing. I'd love if you could show us what your app does and give us a quick demo of how it works and how something like this could potentially make $400,000 a month. This is our app. This is Gravel. We're an AI fitness app specifically designed for strength training and gym workouts. This is the screen you'll see when you first download the app. So, this is our landing screen. We get your name and then we'll just go and ask you a series of questions like why you want to use a fitness app. We ask you about your experience. Let's say I'm an advanced

[00:09:58] user. Depending on on your level, we'll ask more specific questions like what's your one rep max for certain exercises, your goals, ask you about your training frequency, your working split, like we use AI here and there. Make sure that you are showing the users that this is an AI app cuz that's sales. Now, again, more questions specific to how you want to train excluded muscles and focus muscle help us, you know, design the workout towards something that you kind of like. Where do you train? cuz like [snorts] I said, we adapt to your gyms and anywhere you train. So, here is

[00:10:32] where you could create kind of that gym profile. This kind of screen where we generate and show the user that we're generating a custom workout. You get to this final screen where you get your plan kind of summary. Here we go. Hard payw wall before you sign in for the first time. It's like how many users are actually going to pay before they actually see their product. And the answer is a lot. This is what you see when you first open the app. The main thing is the workout card. That's the main thing about the app. That's 90% of your flow is going to be within the

[00:11:03] active workout. Here you just get a list of exercises that you need to do. From here on is like kind of works like a workout tracker. We have proper content for every video. We have a description and how to do each exercises. And then we have a lot of smart AI features like you know if you sort exercises the weights are adjusted based on the order that there are. The app is pretty complete in terms of everything you need to do at the gym. Also things like recovery rate uh will tell you how tired or not your muscles are based on your previous workout and that includes

[00:11:40] external workouts from Apple Health, from Straa, it could be runs, it could be anything. We'll learn from that and we'll adapt your workouts accordingly. And one of the important thing that we grew a lot with this and that was our support. So we have a 247 support chat inside the app and that includes everything from articles to messages and we'll have someone reply an actual person not an AI. That's something that users value a lot. That's pretty much On a similar note I'm curious what's your tech stack? How did you build this app? We use uh React Native and Expo.

[00:12:16] For the back end, I did.NET for most of the core functionality. I've also used Next and React to build some like internal admin dashboards. In terms of AI, so I try to stay kind of niche with the what I use cursor a lot, but I'm very specific which files to touch and don't let the AI just go [music] rogue basically. Yeah. Hey guys, Julian here with a little async update from the future. We finished recording the video and realized that we didn't really go into um numbers and financials of the business. Obviously, very important for you to know and I'm also happy to share

[00:12:50] some of them. Our expense number one is Meta and Tik Tok and then [music] maybe a little bit of Google, maybe a little bit of Apple search. I'd say a third is somehow accurate. A third of our revenue that is. This doesn't include making the ads but just the cost of running them. Expense number two is salaries. It was mainly just the three of us for a first year. I did the development and then Matias and Aaron did the growth and ads.

[00:13:17] Since then, we've grown the team to probably maybe 13 to 14 people, give or take. There's some like part-times. There's some contractors. I'd say somewhere between 50 and [music] 80K. Obviously, let's not forget the 15% from Apple. Revenue cut. It's a 1% clip from revenue as well. We have MMPS, which is maybe a grand a month. And then in terms of infrastructure for running the actual app like servers and AI bills and other tools, I'd say around a grand a [music] month as well.

[00:13:49] The last question that I want to ask you and what we ask all founders who come on Starter Story, what would be your advice to anyone watching this right now that wants to build something? Be proud of what you build. Cuz at least for me, the motivation that comes from building something that I'm excited about can't be matched by anything else. It's always easier to grind and work for zero dollars when you love what you're doing. Another thing will be to keep pushing then don't give up too soon.

[00:14:15] It's a long road. So building it is just not even half of it. Be ready to do all the hustling of you know the Reddit stuff that I did for example and then having ads that don't work and you're going to get some punches. So you need to know that you just need to keep going. And in saying that, it's also knowing when to when to give up actually when you're like, "All right, this product doesn't work." So that's also a very important thing. In our case was our previous startup. We probably dragged that for an extra year. We should have probably called it days like

[00:14:49] way earlier. Well, that's great advice. Thank you, Julian, for coming on to the channel. Thank you, Pat. Thanks for the time. What I love about Julian's story is his app is crushing it. is making over $400,000 a month, but also it's something he's super passionate about. Julian clearly loves fitness and working out, and how cool is it that you get to build an app that makes hundreds of thousands of people's lives better, and it's something that you love, too. That is exactly why we launched Starter Story Build so you can do the same in Starter Story Build. We will help you ship your

[00:15:18] idea to the real world in just a couple weeks, as long as you are ready to actually launch your product. So, if you are, head to the link in the description to check out Starter Story Build. That's it for this episode of Starter Story. Thank you guys for watching. I'll see you in the next one. Peace.

## Links mentioned in the description

- [SMB Leader](https://clickhubspot.com/4d74f4) - [local notes](../../links/channel/smb-leader.md)
- [Turn Your Idea Into A Real App Using Only AI](https://build.starterstory.com/build/ai-build-accelerator?utm_source=youtube&utm_campaign=juliangravl) - [local notes](../../links/channel/turn-your-idea-into-a-real-app-using-only-ai.md)
- [Julian Gargicevich (@julian_gargi) on X](https://x.com/julian_gargi) - [local notes](../../links/video/julian-gargicevich-julian-gargi-on-x.md)
- [Starter Story Build on YouTube](https://www.youtube.com/@StarterStoryBuild) - [local notes](../../links/channel/starter-story-build-on-youtube.md)
- [Starter Story Jobs](https://www.starterstory.com/jobs) - [local notes](../../links/channel/starter-story-jobs.md)
