import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import figureSizes from '../content/figures.generated.json'

const sizes = figureSizes as Record<string, number[]>

export function Markdown({ children }: { children: string }) {
  return (
    <div className="md">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ children }) => (
            <div className="table-wrap">
              <table>{children}</table>
            </div>
          ),
          // Рисунок открывается в полном размере по нажатию: на телефоне подписи мелкие.
          img: ({ src, alt }) => (
            <a href={typeof src === 'string' ? src : undefined} target="_blank" rel="noreferrer">
              <img
                src={typeof src === 'string' ? src : undefined}
                alt={alt ?? ''}
                loading="lazy"
                width={typeof src === 'string' ? sizes[src]?.[0] : undefined}
                height={typeof src === 'string' ? sizes[src]?.[1] : undefined}
              />
            </a>
          ),
          a: ({ href, children }) =>
            href?.startsWith('#/') ? (
              <a href={href}>{children}</a>
            ) : (
              <a href={href} target="_blank" rel="noreferrer">
                {children}
              </a>
            ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
