import { useInfiniteQuery } from '@tanstack/react-query'
import { Heart, MessageSquare } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { AuthRequired } from '../components/AuthRequired'
import { useAuth } from '../context/AuthContext'
import { fetchCommunityProfilePage } from '../services/api'

function formatCommunityDate(value: string) {
  return new Date(value).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

export function CommunityProfilePage() {
  const { username = '' } = useParams()
  const { user, loading } = useAuth()

  const profileQuery = useInfiniteQuery({
    queryKey: ['community-profile-page', username],
    queryFn: ({ pageParam = 0 }) => fetchCommunityProfilePage(username, pageParam, 10),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.next_offset ?? undefined,
    enabled: Boolean(user && username),
  })

  if (loading) {
    return <section className="panel"><p>Loading account...</p></section>
  }

  if (!user) {
    return <AuthRequired message="Sign in to browse community profiles and plant posts." />
  }

  const firstPage = profileQuery.data?.pages[0]
  const profile = firstPage?.profile
  const posts = profileQuery.data?.pages.flatMap((page) => page.posts) ?? []

  return (
    <div className="grid-layout community-layout">
      <section className="panel spotlight page-panel-full profile-hero">
        <div className="spotlight-content">
          <div className="panel-intro">
            <p className="eyebrow">Community Profile</p>
            <h2>{profile?.display_name ?? 'Loading profile...'}</h2>
            <p className="section-copy">@{profile?.username ?? username}</p>
            <p className="section-copy">{profile?.bio ?? 'No bio yet.'}</p>
          </div>
          <div className="metric-row compact">
            <article><strong>{posts.length}</strong><span>Posts loaded</span></article>
            <article><strong>{posts.reduce((sum, post) => sum + post.like_count, 0)}</strong><span>Total likes</span></article>
            <article><strong>{posts.reduce((sum, post) => sum + post.comment_count, 0)}</strong><span>Total comments</span></article>
          </div>
        </div>
      </section>

      <section className="panel page-panel-full community-feed">
        <div className="section-head">
          <div>
            <p className="eyebrow">Posts</p>
            <h3>Shared updates from this grower</h3>
          </div>
          <Link to="/community" className="button-link">Back to feed</Link>
        </div>
        <p className="section-copy community-feed-intro">An authored archive of plant observations, photos, and care milestones.</p>
        <div className="community-feed-list">
          {posts.length === 0 ? <p className="muted">No posts yet.</p> : null}
          {posts.map((post) => (
            <article key={post.id} className="community-post-card">
              <div className="community-post-head">
                <div className="community-profile-mini">
                  <div className="community-avatar imageless">{post.author.display_name.slice(0, 1).toUpperCase()}</div>
                  <div>
                    <strong>{post.author.display_name}</strong>
                    <p>@{post.author.username} · {formatCommunityDate(post.created_at)}</p>
                  </div>
                </div>
              </div>
              <p className="community-post-body">{post.body}</p>
              {post.image_url ? <div className="community-post-image-wrap"><img src={post.image_url} alt="Community plant post" className="community-post-image" /></div> : null}
              <div className="community-post-actions profile-readonly">
                <div className="community-action"><Heart size={16} /><span>{post.like_count}</span></div>
                <div className="community-action"><MessageSquare size={16} /><span>{post.comment_count}</span></div>
              </div>
            </article>
          ))}
        </div>
        {profileQuery.hasNextPage ? <button className="community-load-more" onClick={() => profileQuery.fetchNextPage()} disabled={profileQuery.isFetchingNextPage}>{profileQuery.isFetchingNextPage ? 'Loading...' : 'Load more posts'}</button> : null}
      </section>
    </div>
  )
}
