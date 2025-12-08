"""Seed script to import initial site content data."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.repositories.db import engine_factory, get_session
from app.models.models import Base, SiteContent


def run():
    """Import initial site content data"""
    engine = engine_factory()
    Base.metadata.create_all(bind=engine)
    
    with next(get_session()) as db:
        # Check if content already exists
        if db.query(SiteContent).count() > 0:
            print("Site content already exists. Skipping seed.")
            return
        
        print("Importing site content...")
        
        # Slider items
        sliders = [
            SiteContent(
                SectionKey='slider_1',
                SectionName='اسلایدر 1',
                Title='طراحی خلاقانه',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ<br>و با استفاده از طراحان گرافیک است',
                ImageUrl='/static/img/slider/10.jpg',
                LinkUrl='#',
                LinkText='اکنون خرید کنید',
                SortOrder=1,
                IsActive=True
            ),
            SiteContent(
                SectionKey='slider_2',
                SectionName='اسلایدر 2',
                Title='طراحی خلاقانه',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ<br>و با استفاده از طراحان گرافیک است',
                ImageUrl='/static/img/slider/11.jpg',
                LinkUrl='#',
                LinkText='اکنون خرید کنید',
                SortOrder=2,
                IsActive=True
            ),
            SiteContent(
                SectionKey='slider_3',
                SectionName='اسلایدر 3',
                Title='طراحی خلاقانه',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ<br>و با استفاده از طراحان گرافیک است',
                ImageUrl='/static/img/slider/2.jpg',
                LinkUrl='#',
                LinkText='اکنون خرید کنید',
                SortOrder=3,
                IsActive=True
            ),
        ]
        
        # About section
        about = SiteContent(
            SectionKey='about',
            SectionName='درباره شرکت',
            Title='درباره <span>شرکت</span>',
            Content='<p>لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است </p><p>لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است </p><p>لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است </p>',
            ImageUrl='/static/img/about.jpg',
            Field1='دفتر کانادا',
            SortOrder=1,
            IsActive=True
        )
        
        # Services title
        services_title = SiteContent(
            SectionKey='services_title',
            SectionName='عنوان بخش خدمات',
            Title='دیگر <span>خدمات</span>',
            SortOrder=1,
            IsActive=True
        )
        
        # Services
        services = [
            SiteContent(
                SectionKey='service_1',
                SectionName='خدمات 1 - معماری',
                Title='معماری',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است ',
                ImageUrl='/static/img/icons/icon-1.png',
                Field1='01',
                SortOrder=1,
                IsActive=True
            ),
            SiteContent(
                SectionKey='service_2',
                SectionName='خدمات 2 - طراحی داخلی',
                Title='طراحی داخلی',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است ',
                ImageUrl='/static/img/icons/icon-2.png',
                Field1='02',
                SortOrder=2,
                IsActive=True
            ),
            SiteContent(
                SectionKey='service_3',
                SectionName='خدمات 3 - طراحی شهری',
                Title='طراحی شهری',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است ',
                ImageUrl='/static/img/icons/icon-3.png',
                Field1='03',
                SortOrder=3,
                IsActive=True
            ),
        ]
        
        # Contact sections
        contact_title = SiteContent(
            SectionKey='contact_title',
            SectionName='عنوان بخش تماس',
            Title='تماس با  <span>ما</span>',
            SortOrder=1,
            IsActive=True
        )
        
        contact_info = SiteContent(
            SectionKey='contact_info',
            SectionName='اطلاعات تماس',
            Content='<p>لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است </p>',
            SortOrder=1,
            IsActive=True
        )
        
        contact_reg = SiteContent(
            SectionKey='contact_reg',
            SectionName='کد ثبت',
            Field1='IR002323065B06',
            SortOrder=1,
            IsActive=True
        )
        
        contact_details = SiteContent(
            SectionKey='contact_details',
            SectionName='جزئیات تماس',
            Field1='+98 203-123-0606',  # Phone
            Field2='architecture@gmail.com',  # Email
            Field3='ایران-مشهد-بلوار سجاد',  # Address
            SortOrder=1,
            IsActive=True
        )
        
        # Promo video
        promo_video = SiteContent(
            SectionKey='promo_video',
            SectionName='ویدیوی تبلیغاتی',
            Title='مشاهده ویدیوی تبلیغاتی',
            VideoUrl='https://youtu.be/RziCmLzpFNY',
            SortOrder=1,
            IsActive=True
        )
        
        # Testimonials title
        testimonials_title = SiteContent(
            SectionKey='testimonials_title',
            SectionName='عنوان بخش نظرات',
            Title='آنچه (مشتریان) می گویند؟',
            SortOrder=1,
            IsActive=True
        )
        
        # Testimonials
        testimonials = [
            SiteContent(
                SectionKey='testimonial_1',
                SectionName='نظر مشتری 1',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است ',
                ImageUrl='/static/img/team/1.jpg',
                Field1='آدام همتی',  # Author name
                Field2='مشتری',  # Author role
                SortOrder=1,
                IsActive=True
            ),
            SiteContent(
                SectionKey='testimonial_2',
                SectionName='نظر مشتری 2',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است ',
                ImageUrl='/static/img/team/2.jpg',
                Field1='آدام همتی',  # Author name
                Field2='مشتری',  # Author role
                SortOrder=2,
                IsActive=True
            ),
            SiteContent(
                SectionKey='testimonial_3',
                SectionName='نظر مشتری 3',
                Content='لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است ',
                ImageUrl='/static/img/team/4.jpg',
                Field1='آدام همتی',  # Author name
                Field2='مشتری',  # Author role
                SortOrder=3,
                IsActive=True
            ),
        ]
        
        # Add all content to database
        all_content = (
            sliders + 
            [about, services_title] + 
            services + 
            [contact_title, contact_info, contact_reg, contact_details] + 
            [promo_video, testimonials_title] + 
            testimonials
        )
        
        db.add_all(all_content)
        db.commit()
        
        print(f"Successfully imported {len(all_content)} site content items.")


if __name__ == '__main__':
    run()
