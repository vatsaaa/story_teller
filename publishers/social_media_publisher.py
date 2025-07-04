#!/usr/bin/env python3
"""
Social Media Publishing Script

This script allows you to publish content to various social media platforms
using the Story Teller publishers.

Usage:
    python social_media_publisher.py [options]

Example:
    python social_media_publisher.py --platforms twitter,instagram --text "Hello World" --images image1.jpg
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from publishers.PublisherFactory import PublisherFactory
from publishers.IPublisher import PublisherType
from exceptions.ConfigurationException import ConfigurationException
from exceptions.PublishingException import PublishingException

def load_credentials_from_env() -> Dict[str, Dict[str, str]]:
    """Load credentials from environment variables."""
    return {
        'twitter': {
            'api_key': os.getenv('TWITTER_API_KEY', ''),
            'api_secret': os.getenv('TWITTER_API_SECRET', ''),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN', ''),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        },
        'instagram': {
            'access_token': os.getenv('IG_ACCESS_TOKEN', ''),
            'business_account_id': os.getenv('IG_BUSINESS_ACCOUNT_ID', '')
        },
        'threads': {
            'access_token': os.getenv('THREADS_ACCESS_TOKEN', ''),
            'user_id': os.getenv('THREADS_USER_ID', '')
        },
        'facebook': {
            'page_id': os.getenv('FACEBOOK_PAGE_ID', ''),
            'access_token': os.getenv('FBIG_ACCESS_TOKEN', '')
        },
        'youtube': {
            'client_secrets_file': os.getenv('YOUTUBE_CLIENT_SECRETS_FILE', 'client_secret.json')
        }
    }

def get_publisher_type(platform: str) -> PublisherType:
    """Convert platform string to PublisherType enum."""
    platform_map = {
        'twitter': PublisherType.TWITTER,
        'instagram': PublisherType.INSTAGRAM,
        'threads': PublisherType.THREADS,
        'facebook': PublisherType.FACEBOOK,
        'youtube': PublisherType.YOUTUBE
    }
    
    if platform.lower() not in platform_map:
        raise ValueError(f"Unsupported platform: {platform}")
    
    return platform_map[platform.lower()]

def create_publisher(platform: str, credentials: Dict[str, Dict[str, str]]):
    """Create a publisher for the specified platform."""
    publisher_type = get_publisher_type(platform)
    platform_credentials = credentials.get(platform.lower(), {})
    
    try:
        if platform.lower() == 'facebook':
            page_id = platform_credentials.get('page_id')
            if not page_id:
                raise ConfigurationException(
                    f"Facebook page_id is required",
                    config_key="FACEBOOK_PAGE_ID",
                    details={"platform": "Facebook"}
                )
            return PublisherFactory.create_publisher(publisher_type, page_id=page_id)
        else:
            return PublisherFactory.create_publisher(publisher_type, credentials=platform_credentials)
    
    except ConfigurationException as e:
        print(f"❌ Configuration error for {platform}: {e}")
        return None
    except Exception as e:
        print(f"❌ Failed to create {platform} publisher: {e}")
        return None

def prepare_content(args) -> Dict[str, Any]:
    """Prepare content dictionary from command line arguments."""
    content = {
        "text": {
            "title": args.title or "Story Content",
            "english": args.text or "",
            "hindi": args.hindi_text or ""
        },
        "images": args.images or [],
        "videos": args.videos or [],
        "audios": args.audios or []
    }
    return content

def publish_to_platform(platform: str, content: Dict[str, Any], credentials: Dict[str, Dict[str, str]]) -> bool:
    """Publish content to a specific platform."""
    print(f"\n🚀 Publishing to {platform.upper()}...")
    
    publisher = create_publisher(platform, credentials)
    if not publisher:
        return False
    
    try:
        # Login to the platform
        publisher.login()
        print(f"✅ Successfully logged in to {platform}")
        
        # Publish content
        publisher.publish(content)
        print(f"✅ Successfully published to {platform}")
        
        # Logout
        publisher.logout()
        
        return True
    
    except ConfigurationException as e:
        print(f"❌ Configuration error for {platform}: {e}")
        print(f"💡 Solution: {e.details.get('solution', 'Check your configuration')}")
        return False
    except PublishingException as e:
        print(f"❌ Publishing failed for {platform}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error for {platform}: {e}")
        return False

def main():
    """Main function to handle command line arguments and publish content."""
    parser = argparse.ArgumentParser(
        description="Publish content to various social media platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Publish text to Twitter
    python social_media_publisher.py --platforms twitter --text "Hello World!"
    
    # Publish to multiple platforms with images
    python social_media_publisher.py --platforms twitter,instagram,facebook --text "Check out this story!" --images image1.jpg image2.jpg
    
    # Publish video to YouTube
    python social_media_publisher.py --platforms youtube --title "My Story Video" --text "Description here" --videos video.mp4
    
    # Load content from JSON file
    python social_media_publisher.py --platforms instagram --content-file story_content.json
    
    # Publish to all platforms
    python social_media_publisher.py --all --title "My Story" --text "Check out this amazing story!" --images image1.jpg
        """
    )
    
    # Platform selection arguments (mutually exclusive)
    platform_group = parser.add_mutually_exclusive_group(required=True)
    platform_group.add_argument(
        '--platforms',
        help='Comma-separated list of platforms (twitter,instagram,threads,facebook,youtube)'
    )
    platform_group.add_argument(
        '--all',
        action='store_true',
        help='Publish to all available platforms (twitter,instagram,threads,facebook,youtube)'
    )
    
    # Content arguments
    parser.add_argument('--title', help='Title for the content')
    parser.add_argument('--text', help='Main text content in English')
    parser.add_argument('--hindi-text', help='Main text content in Hindi')
    parser.add_argument('--images', nargs='*', help='List of image file paths')
    parser.add_argument('--videos', nargs='*', help='List of video file paths')
    parser.add_argument('--audios', nargs='*', help='List of audio file paths')
    
    # Alternative content loading
    parser.add_argument('--content-file', help='JSON file containing content data')
    
    # Options
    parser.add_argument('--dry-run', action='store_true', help='Show what would be published without actually publishing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Load credentials
    credentials = load_credentials_from_env()
    
    # Prepare content
    if args.content_file:
        if not os.path.exists(args.content_file):
            print(f"❌ Content file not found: {args.content_file}")
            sys.exit(1)
        
        try:
            with open(args.content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in content file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading content file: {e}")
            sys.exit(1)
    else:
        content = prepare_content(args)
    
    # Validate content
    if not content.get('text', {}).get('english') and not content.get('text', {}).get('hindi'):
        print("❌ At least one text content (English or Hindi) is required")
        sys.exit(1)
    
    # Parse platforms
    if args.all:
        platforms = ['twitter', 'instagram', 'threads', 'facebook', 'youtube']
        print("🌐 Publishing to all platforms")
    else:
        platforms = [p.strip().lower() for p in args.platforms.split(',')]
    
    # Validate platforms
    supported_platforms = ['twitter', 'instagram', 'threads', 'facebook', 'youtube']
    for platform in platforms:
        if platform not in supported_platforms:
            print(f"❌ Unsupported platform: {platform}")
            print(f"💡 Supported platforms: {', '.join(supported_platforms)}")
            sys.exit(1)
    
    # Show what will be published
    print("📝 Content to be published:")
    print(f"   Title: {content.get('text', {}).get('title', 'N/A')}")
    print(f"   English Text: {content.get('text', {}).get('english', 'N/A')[:100]}...")
    print(f"   Hindi Text: {content.get('text', {}).get('hindi', 'N/A')[:100]}...")
    print(f"   Images: {len(content.get('images', []))} files")
    print(f"   Videos: {len(content.get('videos', []))} files")
    print(f"   Audios: {len(content.get('audios', []))} files")
    if args.all:
        print(f"   Platforms: ALL ({', '.join(platforms)})")
    else:
        print(f"   Platforms: {', '.join(platforms)}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No actual publishing will occur")
        return
    
    # Confirm before publishing
    if not args.verbose:
        platform_text = "ALL platforms" if args.all else f"{len(platforms)} platform(s)"
        confirm = input(f"\n❓ Do you want to proceed with publishing to {platform_text}? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Publishing cancelled")
            return
    
    # Publish to each platform
    successful_platforms = []
    failed_platforms = []
    
    for platform in platforms:
        success = publish_to_platform(platform, content, credentials)
        if success:
            successful_platforms.append(platform)
        else:
            failed_platforms.append(platform)
    
    # Summary
    print("\n📊 Publishing Summary:")
    if successful_platforms:
        print(f"✅ Successfully published to: {', '.join(successful_platforms)}")
    
    if failed_platforms:
        print(f"❌ Failed to publish to: {', '.join(failed_platforms)}")
    
    print(f"\n🎯 Total: {len(successful_platforms)}/{len(platforms)} platforms successful")

if __name__ == "__main__":
    main()
