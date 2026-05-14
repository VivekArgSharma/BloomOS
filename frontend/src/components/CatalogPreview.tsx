import type { CatalogItem } from '../types'

type Props = {
  items: CatalogItem[]
}

export function CatalogPreview({ items }: Props) {
  return (
    <section className="panel">
      <div className="section-head">
        <div>
          <p className="eyebrow">Preloaded Catalog</p>
          <h3>50 common horticulture plants ready to use</h3>
        </div>
        <span className="pill">Gemini optional</span>
      </div>
      <div className="catalog-grid">
        {items.slice(0, 12).map((item) => (
          <article key={item.id} className="catalog-card">
            <p>{item.common_name}</p>
            <span>{item.species_name}</span>
            <small>{item.care_profile.light}</small>
          </article>
        ))}
      </div>
    </section>
  )
}
