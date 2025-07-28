## Overview

### Introduction

---

Les Mills Content Portal API provides access to content, video metadata, and enables partners to download digital assets programmatically.

This document outlines the following information:

- Rate Limits and Proper Usage
- API Provider & SDK
- Obtaining Access
- API Specification

<!-- theme: info -->

> Our API is designed to simplify access to LM content and resources while enabling the scheduled synchronization of content and video metadata with your backend systems.<br><br> Les Mills provides support for the implementation of Les Mills Content only. For assistance with API integration or the development of custom solutions, we recommend working with your internal technical team or engaging external third-party technical resources.

### Rate Limits and Proper Usage

---

Video content is released on a quarterly basis. Therefore, we recommend client applications make their requests and updates around the same time as the release date.

#### What this API is for?

This API is provided for synchronizing content and video metadata to partner's backend systems on a scheduled basis.

https://cms.content.lesmills.com/ - is used to retrieve video related information, where you can query by videos, releases, programs, instructors and more.

https://api.content.lesmills.com/ - is used to generate signed URL's, downloading a file and other assets.

#### What this API doesn't support?

This API is not meant to be used in a high volume production environment for frequent requests or scenarios like streaming video-on-demand or downloading content on a per end user request basis. This API should not be used with end user applications.

If you have a use case that requires you to implement this API in a customer facing system, please contact Les Mills Support.

Each request will return all of the available data which could lead to responses that are excessive.

We recommend using the offset query parameter for pagination, for example:
?offset=100. See more details on request pagination: https://docs.directus.io/reference/query.html#page.

<!-- theme: info -->

> Excessive usage may result in termination of API access. To mitigate excessive usage we recommend only making API calls to update your content on a weekly or bi-weekly basis.<br>
> Signed streaming URL's are not subject to the excessive usuage recommendation and can be called as many times as required.

### API Provider & SDK

---

Access to the Content Portal API is powered by [Directus CMS](https://docs.directus.io/reference/introduction.html) and allows access via REST or GraphQL. <br>

Cli tools and JavaScript SDK can be found at https://docs.directus.io/guides/sdk/getting-started.html#directus-javascript-sdk.

A comprehensive guide to features available for filtering and sorting ollections via the API is available here: https://docs.directus.io/reference/introduction.html.

### Obtaining Access

---

#### Access Tokens

Static access tokens also known as API tokens, for use with the API can be generated in Content Portal account settings.

Tokens can be obtained by:

1. Clicking on the profile icon in the lower left hand corner of the portal
2. Then clicking the clipboard icon next to “API Token” to copy it

<!-- theme: info -->

> For Partners requiring a shared static access token, please contact Les Mills Support. This applies in a scenario when multiple developers are working with the API and require it to be associated with more than one user account.

#### Permissions

The API endpoints will only show content that the Partner account is licensed to see.

<!-- theme: info -->

> For access to more content or for any access errors, please contact Les Mills Support.

#### Authentication

Access to the API requires an access token as part of the request. There aretwo ways to accomplish this:

- Use the access token (API token) in the request as an Authorization Header
- Use it as a query parameter as part of a GET request

<!-- theme: info -->

> You cannot validate against the API endpoints with a username andpassword. <br>
> Only static access tokens are accepted at this time, those being the API token and the Directus User ID.

More information can be found here: https://docs.directus.io/reference/authentication.html#access-tokens

### Collection Endpoints

---

- `/Video` : Lists of all available videos.

- `/Program` : Lists all programs available.

- `/Instructors` : Lists all instructors available.

- `/Equipment` : A listing of equipment that is needed for each video.

#### Examples

Request to get a video:

<!--

title: "Get a video:"

lineNumbers: true

-->

```js
GET https://cms.content.lesmills.com/items/Video/?access_token={token}
```

Results can be also expanded by requesting additional fields:

<!--

title: "Get additional fields:"

lineNumbers: true

-->

```js
GET https://cms.content.lesmills.com/items/Video/?fields=*.*&access_token={token}
```

Parsing sample response:

<!--

title: "Directus SDK:  Access using collection name “Video”"

lineNumbers: true

-->

```js

const result = await client.request(readItems(‘Video’, {
    sort: ['title'], fields: '*.*', filter: {
    status: {
        "_eq": 'published',
        "id": "002ee1d5-d55d-48a6-8d9b-a7e4ff8e7861",
        "title": "LES MILLS GRIT 45 STRENGTH (30min)",
        "duration": 30,  // duration in minutes
        "raw_video_file": "17edb646-b6cb-4b5d-beac-ebd6d256fcaa", // UUID of MP4 video file. Needed to download MP4
        "intensity": "High",
        "program": "3f77bba7-29ab-4cd8-a8aa-94d582c3a573", // Program UUID - for example BODYPUMP
        "thumbnail": "7895bd65-d138-4116-b16d-501dbc1d0488", // UUID of video thumbnail PNG or JPG marketing image
        "signed_playback_id": "TTiL01HN007jfA6OMXSFQj9tnGImguLa93eli6Aaelf400", // MUX signed playback ID for HLS streaming support
        "music_file": "561e263f-1cd5-482e-abb1-667e93bf1e02", // UUID of music files used in this release
        "pdf_file": "86497bea-190c-4cda-9a4b-4439f8c51231", // UUID of PDF choreography notes for this video
        "release_file": "002ee1d5-d55d-48a6-8d9b-a7e4ff8e7861", // UUID of ZIP archive containing mp4, thumbnail and captions
        "language": "ES", // language code for this video
        "subtitles": [],
        "equipments": [1108], // Equipment ID available from Equipment endpoint
        "instructors": [6640, 6641, 6642], // Instructor IDs appearing in this video available from Instructor endpoint
    ...
```

### Downloading Assets

---

File download requires:

- File UUID
- Static access token (API Token)
- A request to the download endpoint

Downloads are initiated using a secure request that returns a signed URL.This signed URL grants access to download the file for a limited 24 hour time period and cannot be reused.

Here is an example in JavaScript using fetch:

<!--

title: "Download a signed URL to get authorized access to the file"

lineNumbers: true

-->

```js
const signedURL = await fetch(
  "https://api.content.lesmills.com/v0/file/download?id=" + fileUUID,
  {
    headers: {
      Authorization: `DirectusToken {YOUR_ACCESS_TOKEN}`,
      "User-Agent": `Node.js Downloader`,
      Host: `api.content.lesmills.com`,
    },
  }
);

const signedURLJson = await signedURL.json();

const signedURLString = signedURLJson.location;
```

After obtaining the signed URL, the file can be downloaded using that URL.

Avoid Errors: Copy and paste the entire endpoint URL directly from this documentation. Make sure to maintain the same capitalization for accurate results.
