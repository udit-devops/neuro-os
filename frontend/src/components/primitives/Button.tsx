import React from 'react'

type Variant = 'primary' | 'ghost' | 'danger' | 'outline'
type Size = 'md' | 'sm'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
}

export default function Button({ variant = 'primary', size = 'md', className, ...rest }: ButtonProps) {
  const cls = ['btn', `btn-${variant}`, size === 'sm' ? 'btn-sm' : '']
    .filter(Boolean)
    .join(' ')
  return <button className={className ? `${cls} ${className}` : cls} {...rest} />
}