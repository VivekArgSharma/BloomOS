import { useEffect, useMemo, useState } from 'react'

import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Heart, MessageSquare, Pencil, Send, Trash2, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'

import { AuthRequired } from '../components/AuthRequired'
import { useAuth } from '../context/AuthContext'
import {
  createCommunityComment,
  createCommunityPost,
  deleteCommunityComment,
  deleteCommunityPost,
  fetchCommunityComments,
  fetchCommunityFeed,
  fetchCommunityProfile,
  likeCommunityPost,
  unlikeCommunityPost,
  updateCommunityComment,
  updateCommunityPost,
  updateCommunityProfile,
} from '../services/api'

function formatCommunityDate(value: string) {
  return new Date(value).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

export function CommunityPage() {
  const { user, loading } = useAuth()
  const queryClient = useQueryClient()
  const [body, setBody] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [profileName, setProfileName] = useState('')
  const [profileBio, setProfileBio] = useState('')
  const [expandedPostId, setExpandedPostId] = useState<string | null>(null)
  const [commentDrafts, setCommentDrafts] = useState<Record<string, string>>({})
  const [editingPostId, setEditingPostId] = useState<string | null>(null)
  const [editBody, setEditBody] = useState('')
  const [editImageUrl, setEditImageUrl] = useState('')
  const [editingCommentId, setEditingCommentId] = useState<string | null>(null)

  const feedQuery = useInfiniteQuery({
    queryKey: ['community-feed'],
    queryFn: ({ pageParam = 0 }) => fetchCommunityFeed(pageParam, 10),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.next_offset ?? undefined,
    enabled: Boolean(user),
  })
  const profileQuery = useQuery({ queryKey: ['community-profile'], queryFn: fetchCommunityProfile, enabled: Boolean(user) })

  useEffect(() => {
    if (profileQuery.data) {
      setProfileName(profileQuery.data.display_name)
      setProfileBio(profileQuery.data.bio ?? '')
    }
  }, [profileQuery.data])

  const posts = useMemo(() => feedQuery.data?.pages.flatMap((page) => page.posts) ?? [], [feedQuery.data])

  const createPostMutation = useMutation({
    mutationFn: createCommunityPost,
    onSuccess: () => {
      setBody('')
      setImageUrl('')
      queryClient.invalidateQueries({ queryKey: ['community-feed'] })
    },
  })

  const updatePostMutation = useMutation({
    mutationFn: ({ postId, nextBody, nextImageUrl }: { postId: string; nextBody: string; nextImageUrl?: string }) =>
      updateCommunityPost(postId, { body: nextBody, image_url: nextImageUrl }),
    onSuccess: () => {
      setEditingPostId(null)
      queryClient.invalidateQueries({ queryKey: ['community-feed'] })
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: updateCommunityProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['community-profile'] })
      queryClient.invalidateQueries({ queryKey: ['community-feed'] })
    },
  })

  const likeMutation = useMutation({
    mutationFn: async ({ postId, liked }: { postId: string; liked: boolean }) => liked ? unlikeCommunityPost(postId) : likeCommunityPost(postId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['community-feed'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteCommunityPost,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['community-feed'] }),
  })

  const commentsQuery = useQuery({
    queryKey: ['community-comments', expandedPostId],
    queryFn: () => fetchCommunityComments(expandedPostId ?? ''),
    enabled: Boolean(user && expandedPostId),
  })

  const commentMutation = useMutation({
    mutationFn: ({ postId, commentBody }: { postId: string; commentBody: string }) => createCommunityComment(postId, { body: commentBody }),
    onSuccess: (_, variables) => {
      setCommentDrafts((current) => ({ ...current, [variables.postId]: '' }))
      queryClient.invalidateQueries({ queryKey: ['community-feed'] })
      queryClient.invalidateQueries({ queryKey: ['community-comments', variables.postId] })
    },
  })

  const updateCommentMutation = useMutation({
    mutationFn: ({ commentId, nextBody }: { commentId: string; nextBody: string }) => updateCommunityComment(commentId, { body: nextBody }),
    onSuccess: () => {
      setEditingCommentId(null)
      if (expandedPostId) {
        queryClient.invalidateQueries({ queryKey: ['community-comments', expandedPostId] })
      }
    },
  })

  const deleteCommentMutation = useMutation({
    mutationFn: deleteCommunityComment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['community-feed'] })
      if (expandedPostId) {
        queryClient.invalidateQueries({ queryKey: ['community-comments', expandedPostId] })
      }
    },
  })

  if (loading) {
    return <section className="panel"><p>Loading account...</p></section>
  }

  if (!user) {
    return <AuthRequired message="Sign in to join the BloomOS community, share plant photos via image links, and comment on other growers' posts." />
  }

  return (
    <div className="grid-layout community-layout">
      <section className="panel spotlight community-hero page-panel-full">
        <div className="spotlight-content">
          <div className="panel-intro">
            <p className="eyebrow">Community</p>
            <h2>Share what your plants are doing right now</h2>
            <p className="section-copy">This page keeps the social feature set, but strips away the utilitarian feel. Composer, feed, profile identity, and conversation now behave like one editorial surface.</p>
          </div>
          <div className="metric-row compact community-metrics">
            <article><strong>{posts.length}</strong><span>Loaded posts</span></article>
            <article><strong>{posts.reduce((sum, post) => sum + post.like_count, 0)}</strong><span>Total likes</span></article>
            <article><strong>{posts.reduce((sum, post) => sum + post.comment_count, 0)}</strong><span>Comments</span></article>
          </div>
        </div>
      </section>

      <section className="panel community-composer page-panel-full">
        <div className="section-head"><div><p className="eyebrow">Create Post</p><h3>Share a plant update</h3></div></div>
        <div className="panel-content-split">
          <div className="panel-intro">
            <p className="section-copy">Use an external image URL instead of file uploads. Public HTTPS image links only.</p>
            <Link to={profileQuery.data ? `/community/profile/${profileQuery.data.username}` : '/community'} className="community-profile-mini community-profile-link">
              <div className="community-avatar">{(profileQuery.data?.display_name ?? user.email ?? 'P').slice(0, 1).toUpperCase()}</div>
              <div>
                <strong>{profileQuery.data?.display_name ?? user.email}</strong>
                <p>@{profileQuery.data?.username ?? 'loading-profile'}</p>
              </div>
            </Link>
          </div>
          <div className="form-panel">
            <div className="field-group">
              <label className="field-label" htmlFor="community-body">Post text</label>
              <textarea id="community-body" value={body} onChange={(event) => setBody(event.target.value)} placeholder="My monstera finally pushed a new leaf after I moved it closer to filtered light..." rows={4} />
            </div>
            <div className="field-group">
              <label className="field-label" htmlFor="community-image-url">Plant image URL</label>
              <input id="community-image-url" value={imageUrl} onChange={(event) => setImageUrl(event.target.value)} placeholder="https://..." />
            </div>
            <button onClick={() => createPostMutation.mutate({ body, image_url: imageUrl || undefined })} disabled={!body.trim() || createPostMutation.isPending}>
              {createPostMutation.isPending ? 'Posting...' : 'Publish post'}
            </button>
          </div>
        </div>
      </section>

      <section className="panel community-profile-card">
        <div className="section-head"><div><p className="eyebrow">Your Profile</p><h3>Control how you appear</h3></div></div>
        <div className="form-panel">
          <div className="field-group"><label className="field-label" htmlFor="profile-name">Display name</label><input id="profile-name" value={profileName} onChange={(event) => setProfileName(event.target.value)} /></div>
          <div className="field-group"><label className="field-label" htmlFor="profile-bio">Bio</label><textarea id="profile-bio" value={profileBio} onChange={(event) => setProfileBio(event.target.value)} rows={3} /></div>
          <button onClick={() => updateProfileMutation.mutate({ display_name: profileName || undefined, bio: profileBio || undefined })} disabled={updateProfileMutation.isPending}>{updateProfileMutation.isPending ? 'Saving...' : 'Save profile'}</button>
        </div>
      </section>

      <section className="panel community-feed page-panel-full">
        <div className="section-head"><div><p className="eyebrow">Community Feed</p><h3>Latest plant updates</h3></div></div>
        <div className="community-feed-list">
          {posts.length === 0 ? <p className="muted">No community posts yet. Be the first person to share one.</p> : null}
          {posts.map((post) => {
            const isExpanded = expandedPostId === post.id
            const comments = isExpanded ? commentsQuery.data ?? [] : []
            const isEditingPost = editingPostId === post.id
            return (
              <article key={post.id} className="community-post-card">
                <div className="community-post-head">
                  <Link to={`/community/profile/${post.author.username}`} className="community-profile-mini community-profile-link">
                    <div className="community-avatar imageless">{post.author.display_name.slice(0, 1).toUpperCase()}</div>
                    <div>
                      <strong>{post.author.display_name}</strong>
                      <p>@{post.author.username} · {formatCommunityDate(post.created_at)}{post.updated_at ? ' · edited' : ''}</p>
                    </div>
                  </Link>
                  {post.is_owner ? (
                    <div className="community-post-owner-actions">
                      <button type="button" className="icon-only-button" onClick={() => { setEditingPostId(post.id); setEditBody(post.body); setEditImageUrl(post.image_url ?? '') }} aria-label="Edit post"><Pencil size={16} /></button>
                      <button type="button" className="icon-only-button" onClick={() => deleteMutation.mutate(post.id)} aria-label="Delete post"><Trash2 size={16} /></button>
                    </div>
                  ) : null}
                </div>

                {isEditingPost ? (
                  <div className="form-panel community-inline-editor">
                    <textarea value={editBody} onChange={(event) => setEditBody(event.target.value)} rows={4} />
                    <input value={editImageUrl} onChange={(event) => setEditImageUrl(event.target.value)} placeholder="https://..." />
                    <div className="community-inline-actions">
                      <button onClick={() => updatePostMutation.mutate({ postId: post.id, nextBody: editBody, nextImageUrl: editImageUrl || undefined })} disabled={!editBody.trim() || updatePostMutation.isPending}>Save post</button>
                      <button className="ghost-button" onClick={() => setEditingPostId(null)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <p className="community-post-body">{post.body}</p>
                    {post.image_url ? (
                      <div className="community-post-image-wrap">
                        <img src={post.image_url} alt="Community plant post" className="community-post-image" onError={(event) => { event.currentTarget.style.display = 'none' }} />
                      </div>
                    ) : null}
                  </>
                )}

                <div className="community-post-actions">
                  <button type="button" className={post.viewer_has_liked ? 'community-action liked' : 'community-action'} onClick={() => likeMutation.mutate({ postId: post.id, liked: post.viewer_has_liked })}><Heart size={16} /><span>{post.like_count}</span></button>
                  <button type="button" className={isExpanded ? 'community-action active' : 'community-action'} onClick={() => setExpandedPostId(isExpanded ? null : post.id)}><MessageSquare size={16} /><span>{post.comment_count}</span></button>
                </div>

                {isExpanded ? (
                  <div className="community-comments-panel">
                    <div className="community-comments-list">
                      {commentsQuery.isLoading ? <p className="muted">Loading comments...</p> : null}
                      {!commentsQuery.isLoading && comments.length === 0 ? <p className="muted">No comments yet. Start the conversation.</p> : null}
                      {comments.map((comment) => (
                        <div key={comment.id} className="community-comment-item">
                          <div className="community-comment-avatar"><UserRound size={14} /></div>
                          <div className="community-comment-content">
                            <div className="community-comment-topline">
                              <strong>{comment.author.display_name}</strong>
                              <p className="community-comment-meta">@{comment.author.username} · {formatCommunityDate(comment.created_at)}{comment.updated_at ? ' · edited' : ''}</p>
                            </div>
                            {editingCommentId === comment.id ? (
                              <div className="community-inline-editor">
                                <textarea value={commentDrafts[`edit-${comment.id}`] ?? comment.body} onChange={(event) => setCommentDrafts((current) => ({ ...current, [`edit-${comment.id}`]: event.target.value }))} rows={3} />
                                <div className="community-inline-actions">
                                  <button onClick={() => updateCommentMutation.mutate({ commentId: comment.id, nextBody: commentDrafts[`edit-${comment.id}`] ?? comment.body })}>Save</button>
                                  <button className="ghost-button" onClick={() => setEditingCommentId(null)}>Cancel</button>
                                </div>
                              </div>
                            ) : (
                              <p>{comment.body}</p>
                            )}
                          </div>
                          {comment.is_owner && editingCommentId !== comment.id ? (
                            <div className="community-post-owner-actions">
                              <button type="button" className="icon-only-button" onClick={() => { setEditingCommentId(comment.id); setCommentDrafts((current) => ({ ...current, [`edit-${comment.id}`]: comment.body })) }}><Pencil size={14} /></button>
                              <button type="button" className="icon-only-button" onClick={() => deleteCommentMutation.mutate(comment.id)}><Trash2 size={14} /></button>
                            </div>
                          ) : null}
                        </div>
                      ))}
                    </div>
                    <div className="community-comment-form">
                      <input value={commentDrafts[post.id] ?? ''} onChange={(event) => setCommentDrafts((current) => ({ ...current, [post.id]: event.target.value }))} placeholder="Add a comment..." />
                      <button type="button" onClick={() => commentMutation.mutate({ postId: post.id, commentBody: commentDrafts[post.id] ?? '' })} disabled={!(commentDrafts[post.id] ?? '').trim() || commentMutation.isPending}><Send size={15} /></button>
                    </div>
                  </div>
                ) : null}
              </article>
            )
          })}
        </div>
        {feedQuery.hasNextPage ? <button className="community-load-more" onClick={() => feedQuery.fetchNextPage()} disabled={feedQuery.isFetchingNextPage}>{feedQuery.isFetchingNextPage ? 'Loading...' : 'Load more posts'}</button> : null}
      </section>
    </div>
  )
}
