---
video_id: "4BsxnGRbF4k"
title: "I Found a Business for Sale and Rebuilt It Into $20K/Month"
published: 2025-10-19
duration_seconds: 772
source: https://www.youtube.com/watch?v=4BsxnGRbF4k
transcript_source: YouTube automatic captions (en-orig)
---

# I Found a Business for Sale and Rebuilt It Into $20K/Month

[Watch on YouTube](https://www.youtube.com/watch?v=4BsxnGRbF4k)

## Marketing strategy summary

- Scrape Creators targets developers and businesses that need public social-media and ad-library data but do not want to maintain fragile scrapers, proxies, and outage infrastructure themselves.
- Adrian validated the opportunity before building: an Acquire.com listing showed a scraping API at about $30,000 MRR after three years, with fewer than 100 customers acquired only through SEO; his own three years of scraping experience gave him confidence he could execute.
- His actual early acquisition channel was Twitter: an initial customer arrived after a CTO commented on a post where Adrian scraped the company's site, and Adrian replies to relevant social-scraping launch videos with an offer of 10,000 free API credits.
- The product differentiates through reliable APIs and direct founder support. Adrian says social-media scrapers often break, so he communicates frequently, stays easy to contact, and pays a developer to monitor overnight outages.
- The market supports a concentrated customer base: about 12 customers provide most of the revenue, while roughly 600 people have paid and the service handles almost 20 million API requests per month.
- Monetization is credit-based rather than subscription-based, with packages of $10 for 5,000 credits, $50 for 25,000 credits, and $500 for 500,000 credits. Adrian reports about $20,000 monthly revenue and an 80% margin, with disclosed monthly costs of about $1,500 for proxies, $500 for overnight monitoring, and $400 for servers; because purchases are not recurring, the revenue is not MRR in the subscription sense.

### Reusable playbook

1. Search a business marketplace for SaaS products with proven revenue, using an asking-price floor such as $300,000 or filtering by annual recurring revenue.
2. Limit the search to products that match a skill or market you already understand, then identify the listed business through distinctive listing copy, competitor names, and alternative pages.
3. Reverse-engineer acquisition before building by studying the site, founder profiles, interviews, podcasts, and videos for evidence of where customers come from.
4. Copy the validated concept, not the exact words or implementation, and add a practical edge such as higher reliability, faster support, or a distribution channel you already control.
5. Launch a bare-bones version quickly, seed trials with a concrete free-credit offer where target customers already announce relevant products, and turn those interactions into direct conversations.
6. Improve or promote the same product every day, while tracking revenue concentration, usage, reliability, and costs instead of switching to another idea.

## Transcript

> This transcript was derived from YouTube's English automatic captions. Timestamps mark the start of each caption group. Names and technical terms may contain captioning errors.

[00:00:00] The number one question I get is, "How do I come up with a good business idea?" But the truth is, you don't have to. And this video is proof. Meet Adrian, a solo developer from Austin who had a different approach. I copied a successful app and now it makes me $20,000 a month. A year ago, he saw a successful app for sale, but instead of buying it, he rebuilt it himself and now it makes $20,000 a month.

[00:00:25] If something is working, you have a moral obligation to copy it. I invited Adrian onto the channel to share exactly how he did it, including the specific platform he used to find proven ideas, his method to validate if an idea is worth copying, and the playbook he would use if he had to start over again today. If you've been looking for the right business idea, this episode might change everything for you. I'm Pat Walls, and this is Starter Story.

[00:00:57] All right, Adrian, welcome to the channel. Tell me about who you are, what you built, and what's your story. Hey, my name is Adrian. I'm a soloreneur. I built a SAS to 20K a month. And I found this idea not by coming up with something new, but rather I copied a successful app I found on an online business brokerage and built it Okay, cool. So, you built this API doing $20,000 a month. Can you share a little bit more about some of the numbers behind it?

[00:01:20] Sure. Yeah, so monthly revenue is about 20,000 a month right now. And it is a credit based model. So you just pay for credits and then use them. There's no subscription. So right now we have 600 people who have paid but aren't necessarily paying on a regular basis. We do almost like 20 million API requests a month right now. Okay, cool. Before we get into how you found this idea and kind of the genius way that I think you did it. I do want to understand a little bit more about your background. How do you get to the point where you build a SAS like this?

[00:01:49] So I moved to SF wanting to be a part of tech, learn how to code at this program called App Academy. It was a code boot camp. Then got a job in Utah as an engineer for 3 years, always with the goal of starting my own business. Then quit with $30,000 in savings and then freelanced, built a course, built some products, but didn't have success until I stuck with this one thing, which was scrape creators. And then here we are now. All right, Adrian, what I love about your story is how you came up with this idea and how you validated that this was something that was worth

[00:02:22] building. Before we get into all that, can you share how you even come across the idea to build a web scraping API? Absolutely. One of my followers on Twitter actually DM'd me telling me to check out this listing for Micro Acquire or Acquire.com. And it was a scraping API. And the reason that he DM' me that is because I already had a product that had to do with social media. So, he thought that I might be interested in checking it out. Once I did, I saw the numbers and was completely blown away. I had no confidence myself that a scraping API could make that much money. the fact

[00:02:52] that they were only getting their customers through SEO. I thought this is the product for me. I'm going to do this exact same thing. Okay. So, you see this idea on Micro Acquire, which lists business for sale. You can kind of see how much money is making or how much the business is worth. How do you know that this is something that you could replicate and could potentially be successful?

[00:03:10] Well, a couple of different things. One, I had this skill set because I had been studying scraping for 3 years. So, I had already kind of built those APIs that were hosted on this website. So technically, I had the confidence that I could build it. And then the reason that I thought I could make money off of it was because they were doing 30,000 monthly recurring. They were around for 3 years, only got their customers from SEO, and they had less than 100 customers. So doing that math in my head, I was like, I could probably do that. And I have a little bit of a

[00:03:40] presence on Twitter. So even if I just message people on Twitter, I probably could get there even without SEO. Okay, cool. Well, you find this idea. You think that is something that you could potentially replicate. How do you go about building this? So I am a NodeJS developer. Everything is written in JavaScript. So really it was just a matter of hosting the APIs like on a server. So I had them all in one of my repos. So put those scrapers on a Node.js server on render.com. So then hosted the API there. For the documentation, I just put that actually in a notion doc and then a basic website

[00:04:11] and then that was it. So, it was pretty uh bare bones and it probably took uh just a couple of weeks because I had built that experience and those scrapers for my previous three years of experience and got my first customer a few weeks later. Okay. So, you build this, you get your first customer pretty quickly. I think a lot of people watching this may be similar to you software developer. They have the skills to build something like this. But the hard part is getting customers, growing, scaling this and replicating what this business that you sort of cloned had

[00:04:40] already done. So, how did you grow this business? How did you get customers? Uh, I hang out on Twitter a lot, so people see me there. People have seen my content. My first customer was just because I scraped a company's site and then the CTO actually commented on that post. So, completely accident. And then also, anytime someone has a launch video that has anything to do with scraping social media, then I comment saying, "Hey, I'll give you 10K free credits if you'll try my API." But the great thing about a scraping API also is that you don't have to have a lot of customers to

[00:05:09] have a decent MR. So I have maybe like 12 who pay for the majority of that MR. I love Adrian's strategy for copying successful apps. But here's the thing, he didn't just copy the idea. He got creative and made his idea 1% better than the rest. Nowadays, this creative edge is what separates winners from everyone else. And this is where the HubSpot for Startups Creative AI use cases database comes in handy. It's a free database with over 100 creative ways to use AI in your business. These aren't the obvious AI apps that everyone's already building. These are the creative uses your competitors

[00:05:48] haven't discovered yet that can give you an unfair advantage. My favorite part is the fact that they break down the list by difficulty, business impact, and even steps on how to get started with which tools. Just find the one that resonates with you and run with it. So, if you're ready to join Adrian and start your own SAS business, then download the free AI differentiation database at the first link right below in the description.

[00:06:10] Thank you to HubSpot for Startups for sponsoring this video. Now, let's get back into it. I want to understand a little bit more about this framework. If you were to start over today in 2025 and go to Microacquire and find another idea, how would you do that? For people watching, can you break it down step by step? All right, this will be my playbook if I was doing this again. Step one, you're going to visit the micro acquire marketplace. Step two, filter by SAS. And then step three, filter by asking price. So, we're not looking for apps that aren't making any money.

[00:06:40] That's not great. We're looking for pre-validated ideas. So, increase that asking price to at least 300,000 or you can filter by annual recurring revenue, whatever you want. All right, step four. You're going to look for things that you would be good at or a market that you would know about. For example, I knew I wanted to build a product that had something to do with web scraping. That was my niche. I was niching down for that. You would want to build a product that you have some sort of knowledge about. All right, step five. We're going to try to find the website. Obviously,

[00:07:09] on Microquire, they don't list what the website is, but we're going to reverse engineer and try to find the actual website. So, a lot of these SAS businesses are really easy to find because you can just Google what they have in their listing. So in the title or description, you can just Google part of that and usually they're using like their title or H1 or description actually in the micro acquire description. So it's pretty easy to find or they actually list competitors if you scroll down. So all you have to do a lot of times the website will write blog posts or pages that will say competitor

[00:07:44] name and then alternative. So all you need to Google is the competitor and then alternative or alternatives. One of those two ways will get you to the site and then you can just view the site and see if the copy is similar. Then boom, you got the site. All right, step six. Try to reverse engineer how they acquired customers. This is arguably the most important part. Not so hard to build the product, but how are they getting customers? So, for example, the app that I was copying, I knew that they got their customers mostly from SEO.

[00:08:10] Read everything that you can on the site, any information that they talk about how they're acquiring customers. Try to look up like the founder on Twitter, LinkedIn. Try to find podcasts or YouTube videos, any way that they talk about the product or how to grow the product. Step seven, actually build the damn thing. Step eight, yeah, this is just don't copy word for word. Don't copy everything literally exactly. You just want to copy the concept, the idea.

[00:08:33] Step nine, don't get distracted with other projects. Do something every single day to promote or improve the product. You know that this idea is making money. So now you just have to execute. do something every single day to build the product or market it and I guarantee you will make money. You will be successful. Okay. Thanks Adrian for sharing that full playbook. I think that's awesome.

[00:08:54] We haven't really talked yet about what your API does specifically. You have this sort of micro SASS API. Can you just share what it does, how it works, what type of customers use it? Yeah, so it scrapes specifically social media that can be Instagram, YouTube, Twitter, uh and then we just scrape public data. Got to say that for the lawyers out there. We scrape social media as well as like their ad libraries as well. So the Facebook ad library, LinkedIn ad library, etc. And this obviously helps developers because scraping is a pain in the butt. So we scrape so you don't have to. We handle

[00:09:26] all the infrastructure, proxy rotation, etc. And who uses this tool is a lot of like link and bio tools. Anyone who's tracking analytics like short form content. Yeah. So it's a credit based system. So pay as you go. So we have three payment plans right now. $10 for 5,000 credits, $50 for 25,000, and then 500,000 credits for $500. I think it does well because it works. Like there's a lot of scrapers out there, like social media in particular, that break pretty often. So with mine, I think people like it because it's reliable and then if it's not reliable, then I'll communicate

[00:10:00] with people pretty frequently as well, as well as it's really easy to get a hold of me. Whereas a lot of developers who build these sort of things, you don't even have their email or a way to contact them. Um, so I think that is also helpful. Okay, let's change topics a little bit. I want to understand techstack. You're a developer. You have a scraping pretty technical type of product. How did you build this? What's your tech stack?

[00:10:20] Yeah, honestly, it's pretty straightforward, pretty easy. So everything is written in Node.js JavaScript and it's just a bunch of HTTP requests. So one important thing that I use is this package called impit. It's developed by ampify. So another scraping framework. So you npm install input use that for HTTP requests and then just a lot of proxies. So I have four main ones that I use which are Evomi core residential which are the cheapest residential out there do webshare and massive and then I host everything on render.com or I host subscripts on AWS Lambda obviously I use cursor so that's

[00:10:55] 20 bucks a month and then superbase for the database and then the front end is astro uh plus react and on a similar note I'm also curious what are the costs to use all these tools what does the profit margin look like for your business yeah margin is about 80% Most of it is spent on proxies. So about $1,500 a month right now is spent on proxies. And I hire a developer in the Philippines to monitor the API for outages at night. So he's about $500. And then server costs are about $400. Okay, cool. Thank you for sharing that. Thank you for being transparent about all that. That's

[00:11:26] awesome. Last question that I want to ask. We ask everyone who comes on Starter Story, what would be your advice for anyone watching this starting out in 2025 about how to do something like you've done? Stop bouncing around ideas and just pick one thing. Do it every single day. Focus on it every single day and you'll make it. Stop getting distracted because that's exactly what happened to me.

[00:11:46] Cool. That's amazing. Adrian, thank you for coming on. Thank you for sharing all this, being super transparent. I love the business you built. Thanks for coming on and sharing everything. Thanks, man. Appreciate it. Big thanks to Adrian for coming on to the channel. I love his story because it flips the startup myth on its head. Adrien didn't need to invent something brand new. He just saw a model. He copied it and he executed better and that turned into a SAS that makes $20,000 a month and effectively changed his life. I think the lesson that anyone can take from this is stop waiting for

[00:12:15] that genius idea. Just start, build, and keep improving. And you never know what might happen. This is exactly why we launched Starter Story Build, where we will show you how to take your idea, use AI to build it fast, and launch in just a couple weeks. Even if you're starting with no team, no money, and no clear idea, if you want to finally build your first app, launch it, and potentially turn it into a profitable business, well, head to the first link in the description and check out Starter Story Build. That's it for this episode, guys.

[00:12:43] Thank you for watching. I hope you enjoyed it. We'll see you in the next one. Peace.

## Links mentioned in the description

- [100+ Creative AI Use Cases [The Next Wave + HSFS]](https://clickhubspot.com/0761f2) - [local notes](../../links/channel/100-creative-ai-use-cases-the-next-wave-hsfs.md)
- [Turn Your Idea Into A Real App Using Only AI](https://build.starterstory.com/build/ai-build-accelerator?utm_source=youtube&utm_campaign=adrian) - [local notes](../../links/channel/turn-your-idea-into-a-real-app-using-only-ai.md)
- [Adrian's app](https://scrapecreators.com/) - [local notes](../../links/video/adrian-s-app.md)
- [Adrian | The Web Scraping Guy (@adrian_horning_) on X](https://x.com/adrian_horning_) - [local notes](../../links/video/adrian-the-web-scraping-guy-adrian-horning-on-x.md)
- [Starter Story Build on YouTube](https://www.youtube.com/@StarterStoryBuild) - [local notes](../../links/channel/starter-story-build-on-youtube.md)
- [Starter Story Jobs](https://www.starterstory.com/jobs) - [local notes](../../links/channel/starter-story-jobs.md)
