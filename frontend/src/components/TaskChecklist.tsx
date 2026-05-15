import type { DailyTask } from '../types'

type Props = {
  tasks: DailyTask[]
  onComplete: (taskId: string) => Promise<void>
}

export function TaskChecklist({ tasks, onComplete }: Props) {
  return (
    <section className="panel page-panel-full">
      <div className="section-head">
        <div>
          <p className="eyebrow">Daily Plan</p>
          <h3>Adaptive tasks</h3>
        </div>
      </div>
      <div className="task-list">
        {tasks.map((task) => (
          <button key={task.id} className={task.completed ? 'task-card done' : 'task-card'} onClick={() => onComplete(task.id)}>
            <div>
              <strong>{task.title}</strong>
              <p>{task.description}</p>
            </div>
            <span>{task.completed ? 'Done' : 'Tap to complete'}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
