import type { CatalogItem } from '../types'

type Props = {
  items: CatalogItem[]
}

export function CatalogPreview({ items }: Props) {
  return (
    <section className="panel page-panel-full">
      <div className="section-head">
        <div>
          <p className="eyebrow">Preloaded Catalog</p>
          <h3>50 common horticulture plants ready to use</h3>
        </div>
        <span className="pill">Gemini optional</span>
      </div>
      <p className="section-copy">Reference the built-in library for quick additions, light guidance, and a cleaner starting point before image-based identification.</p>
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
