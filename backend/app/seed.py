from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import JobSource, User, UserRole


async def seed_defaults() -> None:
    async with AsyncSessionLocal() as db:
        src_res = await db.execute(select(JobSource))
        existing_sources = {s.name for s in src_res.scalars().all()}
        
        default_sources = [
            JobSource(name="Remotive", source_type="remotive", enabled=True, config={}),
            JobSource(name="Jobicy", source_type="jobicy", enabled=True, config={}),
            JobSource(name="WeWorkRemotely", source_type="weworkremotely", enabled=True, config={}),
            JobSource(
                name="Python.org Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://www.python.org/jobs/feed/rss/"},
            ),
            JobSource(
                name="Remotive Marketing Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/marketing/feed"},
            ),
            JobSource(
                name="Remotive Support Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/customer-support/feed"},
            ),
            JobSource(
                name="Remotive Product Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/product/feed"},
            ),
            JobSource(
                name="Remotive Sales Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/sales/feed"},
            ),
            JobSource(
                name="Remotive Finance Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/finance/feed"},
            ),
            JobSource(
                name="Remotive HR Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/human-resources/feed"},
            ),
            JobSource(
                name="Remotive Writing Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/writing/feed"},
            ),
            JobSource(
                name="Remotive Design Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://remotive.com/remote-jobs/design/feed"},
            ),
            JobSource(
                name="NoDesk Remote Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://nodesk.co/remote-jobs/index.xml"},
            ),
            JobSource(
                name="JustRemote Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://justremote.co/remote-jobs.rss"},
            ),
            JobSource(
                name="Working Nomads Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://www.workingnomads.com/jobs?format=rss"},
            ),
            JobSource(
                name="DailyRemote Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://dailyremote.com/feed/"},
            ),
            JobSource(
                name="CryptoJobsList",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://cryptojobslist.com/posts.rss"},
            ),
            JobSource(
                name="Jobspresso",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://jobspresso.co/feed/"},
            ),
            JobSource(
                name="Authentic Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://authenticjobs.com/feed/"},
            ),
            JobSource(
                name="Dribbble Creative Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://dribbble.com/jobs.rss"},
            ),
            JobSource(
                name="VueJobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://vuejobs.com/feed.xml"},
            ),
            JobSource(
                name="SkipTheDrive Jobs",
                source_type="rss",
                enabled=True,
                config={"feed_url": "https://www.skipthedrive.com/feed/"},
            ),
            # 🇰🇪 Kenya
            JobSource(name="BrighterMonday Kenya", source_type="brightermonday", enabled=True, config={}),
            JobSource(name="Fuzu Kenya", source_type="fuzu", enabled=True, config={}),
            JobSource(name="MyJobMag Kenya", source_type="myjobmag", enabled=True, config={}),
            JobSource(name="Career Point Kenya", source_type="careerpoint", enabled=True, config={}),
            JobSource(name="JobWeb Kenya", source_type="jobwebkenya", enabled=True, config={}),
            # 🌍 Remote
            JobSource(name="Remote OK", source_type="remoteok", enabled=True, config={}),
            JobSource(name="Remote.co", source_type="remoteco", enabled=True, config={}),
            JobSource(name="Wellfound", source_type="wellfound", enabled=True, config={}),
            JobSource(name="Himalayas", source_type="himalayas", enabled=True, config={}),
            # 🤖 AI/Data
            JobSource(name="TELUS Digital AI", source_type="telusdigital", enabled=True, config={}),
            JobSource(name="RWS AI", source_type="rws", enabled=True, config={}),
            JobSource(name="Outlier AI", source_type="outlier", enabled=True, config={}),
            JobSource(name="Mindrift AI", source_type="mindrift", enabled=True, config={}),
            JobSource(name="Welocalize", source_type="welocalize", enabled=True, config={}),
            JobSource(name="CloudFactory", source_type="cloudfactory", enabled=True, config={}),
            JobSource(name="OneForma", source_type="oneforma", enabled=True, config={}),
            # 💻 Tech/Contract
            JobSource(name="Contra", source_type="contra", enabled=True, config={}),
            JobSource(name="Lemon.io", source_type="lemon", enabled=True, config={}),
            JobSource(name="Arc.dev", source_type="arc", enabled=True, config={}),
            JobSource(name="Turing", source_type="turing", enabled=True, config={}),
        ]
        
        for ds in default_sources:
            if ds.name not in existing_sources:
                db.add(ds)

        admin = await db.execute(select(User).where(User.email == "admin@aijobhunter.local"))
        if not admin.scalar_one_or_none():
            from app.services.auth import create_user

            user = await create_user(db, "admin@aijobhunter.local", "AdminPass123!", "Admin")
            user.role = UserRole.ADMIN
        await db.commit()
