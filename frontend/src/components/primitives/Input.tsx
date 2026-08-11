import React from 'react'

interface InputProps extends React.ComponentProps<'input'> {
  label?: string
}

export default function Input({ label, className, ...rest }: InputProps) {
  return (
    <div>
      {label && <label className="ui-label">{label}</label>}
      <input className={className ? `ui-input ${className}` : 'ui-input'} {...rest} />
    </div>
  )
}