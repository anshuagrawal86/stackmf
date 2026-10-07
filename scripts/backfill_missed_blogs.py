import os
import sys
import datetime
from daily_blog_publisher import publish_single_article, rebuild_site_assets, load_posts
from blogs_data_queue import QUEUED_ARTICLES

SCHEDULE_MAPPING = [
    ("zowe-cli-cics-newcopy-automation-pipeline", "2026-09-29"),
    ("ezt-virtual-files-imu-memory-optimization", "2026-09-30"),
    ("vscode-zowe-jcl-formatting-validation-extension", "2026-10-01"),
    ("idz-telemetry-metrics-developer-productivity-dashboard", "2026-10-02"),
    ("db2-hash-access-vs-index-access-z16", "2026-10-03"),
    ("cics-liberty-java-spring-boot-zero-mlc", "2026-10-04"),
    ("vsam-linear-datasets-lds-db2-internals", "2026-10-05"),
    ("ims-fast-path-dedb-online-utility-tuning", "2026-10-06"),
    ("ca-7-virtual-resource-management-vrm-contention", "2026-10-07")
]

def main():
    existing_posts = load_posts()
    existing_slugs = set(p['slug'] for p in existing_posts)
    
    queued_map = {a['slug']: a for a in QUEUED_ARTICLES}
    published_count = 0

    for slug, date_str in SCHEDULE_MAPPING:
        if slug in existing_slugs:
            print(f"Skipping already published: {slug}")
            continue
        
        target_topic = queued_map.get(slug)
        if not target_topic:
            print(f"Topic {slug} not found in QUEUED_ARTICLES!")
            continue

        print(f"Publishing: {slug} for date {date_str}...")
        art = publish_single_article(target_topic, date_str)
        if art:
            published_count += 1

    if published_count > 0:
        print(f"Rebuilding index, sitemap, and llms with {published_count} new posts...")
        rebuild_site_assets()
        print(f"SUCCESS: Successfully backfilled and published {published_count} daily mainframe blog posts!")
    else:
        print("All target posts already published.")

if __name__ == '__main__':
    main()
