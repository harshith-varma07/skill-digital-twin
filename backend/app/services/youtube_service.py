"""
YouTube Service for video recommendations.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from app.core.config import settings


class YouTubeService:
    """Service for YouTube API interactions and video recommendations."""
    
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance",
        video_duration: Optional[str] = None,
        video_type: str = "video"
    ) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            order: Order by ('relevance', 'viewCount', 'date', 'rating')
            video_duration: Duration filter ('short', 'medium', 'long')
            video_type: Type of video ('video', 'playlist', 'channel')
        
        Returns:
            List of video details
        """
        params = {
            "part": "snippet",
            "q": query + " tutorial",  # Add tutorial for educational content
            "type": video_type,
            "maxResults": max_results,
            "order": order,
            "key": self.api_key,
            "relevanceLanguage": "en",
            "safeSearch": "moderate"
        }
        
        if video_duration:
            params["videoDuration"] = video_duration
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/search", params=params)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            video_ids = [item["id"]["videoId"] for item in data.get("items", []) if "videoId" in item.get("id", {})]
            
            if not video_ids:
                return []
            
            # Get detailed video information
            videos = await self._get_video_details(video_ids)
            return videos
    
    async def _get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information for videos."""
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/videos", params=params)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            videos = []
            
            for item in data.get("items", []):
                video = {
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"][:500],
                    "channel_title": item["snippet"]["channelTitle"],
                    "thumbnail_url": item["snippet"]["thumbnails"].get("high", {}).get("url", ""),
                    "published_at": item["snippet"]["publishedAt"],
                    "duration_seconds": self._parse_duration(item["contentDetails"]["duration"]),
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "url": f"https://www.youtube.com/watch?v={item['id']}"
                }
                videos.append(video)
            
            return videos
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    async def get_learning_videos(
        self,
        topic: str,
        skill_level: str = "beginner",
        max_results: int = 10,
        duration_preference: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Get curated learning videos for a topic.
        
        Args:
            topic: Learning topic
            skill_level: Skill level ('beginner', 'intermediate', 'advanced')
            max_results: Maximum number of videos
            duration_preference: Preferred video duration ('short', 'medium', 'long')
        
        Returns:
            List of curated videos with relevance scores
        """
        # Construct level-appropriate query
        level_keywords = {
            "beginner": "beginner introduction basics",
            "intermediate": "intermediate hands-on practical",
            "advanced": "advanced in-depth expert"
        }
        
        query = f"{topic} {level_keywords.get(skill_level, '')} tutorial course"
        
        # Map duration preference
        duration_map = {
            "short": "short",  # < 4 minutes
            "medium": "medium",  # 4-20 minutes
            "long": "long"  # > 20 minutes
        }
        
        videos = await self.search_videos(
            query=query,
            max_results=max_results * 2,  # Get more to filter
            order="relevance",
            video_duration=duration_map.get(duration_preference)
        )
        
        # Score and rank videos
        scored_videos = []
        for video in videos:
            score = self._calculate_relevance_score(video, topic, skill_level)
            video["relevance_score"] = score
            video["quality_score"] = self._calculate_quality_score(video)
            scored_videos.append(video)
        
        # Sort by combined score
        scored_videos.sort(
            key=lambda v: (v["relevance_score"] * 0.6 + v["quality_score"] * 0.4),
            reverse=True
        )
        
        return scored_videos[:max_results]
    
    def _calculate_relevance_score(
        self,
        video: Dict[str, Any],
        topic: str,
        skill_level: str
    ) -> float:
        """Calculate relevance score for a video."""
        score = 0.5
        title_lower = video["title"].lower()
        desc_lower = video["description"].lower()
        topic_lower = topic.lower()
        
        # Topic presence in title
        if topic_lower in title_lower:
            score += 0.2
        
        # Tutorial/educational indicators
        educational_terms = ["tutorial", "course", "learn", "guide", "explained", "how to"]
        for term in educational_terms:
            if term in title_lower or term in desc_lower:
                score += 0.05
        
        # Skill level match
        if skill_level.lower() in title_lower or skill_level.lower() in desc_lower:
            score += 0.1
        
        # Penalize very short videos for learning
        if video["duration_seconds"] < 120:
            score -= 0.15
        
        # Prefer appropriate length videos
        if 300 <= video["duration_seconds"] <= 1800:  # 5-30 minutes
            score += 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _calculate_quality_score(self, video: Dict[str, Any]) -> float:
        """Calculate quality score based on engagement metrics."""
        score = 0.5
        
        view_count = video.get("view_count", 0)
        like_count = video.get("like_count", 0)
        
        # View count scoring
        if view_count > 1000000:
            score += 0.2
        elif view_count > 100000:
            score += 0.15
        elif view_count > 10000:
            score += 0.1
        elif view_count > 1000:
            score += 0.05
        
        # Like ratio (if we have enough data)
        if view_count > 100 and like_count > 0:
            like_ratio = like_count / view_count
            if like_ratio > 0.05:  # > 5% like rate
                score += 0.15
            elif like_ratio > 0.03:
                score += 0.1
            elif like_ratio > 0.01:
                score += 0.05
        
        return min(max(score, 0.0), 1.0)
    
    async def create_learning_sequence(
        self,
        topic: str,
        subtopics: List[str],
        skill_level: str = "beginner"
    ) -> List[Dict[str, Any]]:
        """
        Create an optimal learning sequence of videos.
        
        Args:
            topic: Main topic
            subtopics: List of subtopics in learning order
            skill_level: Starting skill level
        
        Returns:
            Ordered list of videos forming a learning sequence
        """
        sequence = []
        
        # Get overview video first
        overview_videos = await self.get_learning_videos(
            topic=f"{topic} overview introduction",
            skill_level="beginner",
            max_results=2,
            duration_preference="medium"
        )
        
        if overview_videos:
            overview_videos[0]["sequence_role"] = "introduction"
            sequence.append(overview_videos[0])
        
        # Get videos for each subtopic
        for i, subtopic in enumerate(subtopics):
            # Adjust skill level as we progress
            if i < len(subtopics) // 3:
                level = "beginner"
            elif i < 2 * len(subtopics) // 3:
                level = "intermediate"
            else:
                level = skill_level
            
            videos = await self.get_learning_videos(
                topic=f"{topic} {subtopic}",
                skill_level=level,
                max_results=2,
                duration_preference="medium"
            )
            
            if videos:
                videos[0]["sequence_role"] = f"lesson_{i + 1}"
                videos[0]["subtopic"] = subtopic
                sequence.append(videos[0])
        
        # Add practice/project video
        practice_videos = await self.get_learning_videos(
            topic=f"{topic} project practice exercise",
            skill_level=skill_level,
            max_results=2,
            duration_preference="long"
        )
        
        if practice_videos:
            practice_videos[0]["sequence_role"] = "practice"
            sequence.append(practice_videos[0])
        
        return sequence


# Singleton instance
youtube_service = YouTubeService()
