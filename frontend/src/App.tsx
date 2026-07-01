import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/core/theme-toggle"

export function App() {
  return (
    <div className="flex min-h-svh items-center justify-center p-6">
      <div className="flex w-full max-w-md flex-col gap-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">QuickBite Support</h1>
          <ThemeToggle />
        </div>

        <div className="flex flex-col gap-3 text-sm leading-loose">
          <p>You may now add components and start building.</p>
          <p>We&apos;ve already added the button component for you.</p>
          <Button className="mt-2 w-fit">Get started</Button>
        </div>

        <div className="font-mono text-xs text-muted-foreground">
          (Press <kbd>d</kbd> to toggle dark mode)
        </div>
      </div>
    </div>
  )
}

export default App
