# Publisher Configuration Guide

## Environment Variables Required for Publishers

To enable social media publishing, you need to configure the following environment variables in your `.env` file:

### Facebook Publisher
```bash
FBIG_PAGE_ID=your_facebook_page_id
FBIG_ACCESS_TOKEN=your_facebook_access_token
FBIG_BASE_URL=https://graph.facebook.com/
FBIG_BASE_VER=v18.0/
```

### Instagram Publisher
```bash
IG_ACCESS_TOKEN=your_instagram_access_token
```

### Twitter Publisher
```bash
TWITTER_ACCESS_TOKEN=your_twitter_access_token
```

### YouTube Publisher
```bash
YOUTUBE_ACCESS_TOKEN=your_youtube_access_token
```

## How Publishing Works

1. **Checkbox Selection**: In the Streamlit interface, check the boxes for the social media platforms you want to publish to.

2. **Credential Validation**: The application will check if the required environment variables are set for each selected platform.

3. **Graceful Degradation**: If credentials are missing for a platform, the application will:
   - Show a warning message
   - Skip that platform
   - Continue processing with other configured platforms

4. **Safe Operation**: The story processing will continue even if no publishers are configured.

## Example Output Messages

```
Warning: Facebook publisher credentials not configured. Skipping Facebook publishing.
Warning: Twitter publisher credentials not configured. Skipping Twitter publishing.
Note: No publishers were configured. Story will be processed but not published.
```

## Setting Up Credentials

1. Create accounts and apps for each social media platform
2. Obtain the required API tokens/keys
3. Add them to your `.env` file
4. Restart the Streamlit application
5. Select the platforms you want to publish to

## Troubleshooting

- **ConfigurationException**: Missing or invalid credentials
- **PublishingException**: API errors during publishing
- Check your `.env` file for typos
- Verify your API tokens are still valid
- Ensure you have the necessary permissions for posting
