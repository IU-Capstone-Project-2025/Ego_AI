import React, { useState, useEffect, useCallback } from 'react';
import { format, startOfWeek, addDays, addWeeks, subWeeks, isToday } from 'date-fns';
import './Calendar.css';
import { fetchEvents, createEvent, deleteEvent } from '@/utils/calendarApi';

// Types for our calendar events
interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  type: 'focus' | 'tasks' | 'target' | 'other';
  description?: string;
}

interface TaskForm {
  title: string;
  duration: number;
  type: 'focus' | 'tasks' | 'target' | 'other';
  description: string;
  dueDate: string;
  dueTime: string;
}

export const Calendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [weeklyHours, setWeeklyHours] = useState({
    focus: 0,
    tasks: 0,
    target: 0,
    other: 0,
    free: 119
  });
  const [isLoading, setIsLoading] = useState(false);

  const [taskForm, setTaskForm] = useState<TaskForm>({
    title: '',
    duration: 1,
    type: 'tasks',
    description: '',
    dueDate: format(currentDate, 'yyyy-MM-dd'),
    dueTime: '18:00'
  });

  // Update task form date when currentDate changes
  const updateTaskFormDate = () => {
    setTaskForm(prev => ({
      ...prev,
      dueDate: format(currentDate, 'yyyy-MM-dd')
    }));
  };

  // Calculate hours for each task type in the current week
  const calculateWeeklyHours = useCallback(() => {
    const weekStart = startOfWeek(currentDate);
    const weekEnd = addDays(weekStart, 6);
    const weekEvents = events.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate >= weekStart && eventDate <= weekEnd;
    });
    const hours = { focus: 0, tasks: 0, target: 0, other: 0 };
    weekEvents.forEach(event => {
      const duration = (new Date(event.end).getTime() - new Date(event.start).getTime()) / (1000 * 60 * 60);
      // Patch: если тип невалидный, считаем как 'other'
      const validTypes = ['focus', 'tasks', 'target', 'other'];
      const type = validTypes.includes(event.type) ? event.type : 'other';
      hours[type] += duration;
    });
    const totalWorkHours = hours.focus + hours.tasks + hours.target + hours.other;
    const workingHours = 7 * 17;
    const free = Math.max(0, workingHours - totalWorkHours);
    return { ...hours, free };
  }, [currentDate, events]);

  // Load events from backend
  const loadCalendarEvents = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchEvents();
      // Map backend fields to frontend fields
      const parsed = data.map((event: any) => ({
        ...event,
        start: new Date(event.start_time),
        end: new Date(event.end_time)
      }));
      setEvents(parsed);
    } catch (error) {
      setEvents([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCalendarEvents();
    updateTaskFormDate();
  }, [currentDate, loadCalendarEvents]);

  useEffect(() => {
    setWeeklyHours(calculateWeeklyHours());
  }, [events, calculateWeeklyHours]);

  // Create new task (local API)
  const createTask = async () => {
    if (!taskForm.title.trim()) {
      alert('Please enter a task title');
      return;
    }
    try {
      setIsLoading(true);
      const [hours, minutes] = taskForm.dueTime.split(':');
      const dueDateTime = new Date(taskForm.dueDate);
      dueDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      const endDateTime = new Date(dueDateTime.getTime() + (taskForm.duration * 60 * 60 * 1000));
      const systemDescription = `Duration: ${taskForm.duration}h\nType: ${taskForm.type}`;
      const fullDescription = taskForm.description.trim()
        ? `${taskForm.description}\n\n${systemDescription}`
        : systemDescription;
      const newEvent = {
        title: taskForm.title,
        start: dueDateTime.toISOString(),
        end: endDateTime.toISOString(),
        type: taskForm.type,
        description: fullDescription
      };
      await createEvent(newEvent);
      await loadCalendarEvents();
      setTaskForm({
        ...taskForm,
        title: '',
        description: ''
      });
      alert('Task created successfully!');
    } catch (error) {
      alert('Error creating task. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Удаление задачи
  const handleDeleteEvent = async (eventId: string) => {
    if (!window.confirm('Удалить задачу?')) return;
    setIsLoading(true);
    try {
      await deleteEvent(eventId);
      await loadCalendarEvents();
    } catch (error) {
      alert('Ошибка при удалении задачи.');
    } finally {
      setIsLoading(false);
    }
  };

  // Navigation functions
  const goToPreviousWeek = () => setCurrentDate(subWeeks(currentDate, 1));
  const goToNextWeek = () => setCurrentDate(addWeeks(currentDate, 1));

  // Get week days
  const getWeekDays = () => {
    const start = startOfWeek(currentDate);
    return Array.from({ length: 7 }, (_, i) => addDays(start, i));
  };

  // Time slots (6am to 11pm)
  const timeSlots = Array.from({ length: 18 }, (_, i) => i + 6);

  // Get events that START in this specific hour slot (to avoid duplicates)
  const getEventsForSlot = (day: Date, hour: number) => {
    return events.filter(event => {
      const eventStart = new Date(event.start);
      const eventDate = format(eventStart, 'yyyy-MM-dd');
      const dayDate = format(day, 'yyyy-MM-dd');
      return eventDate === dayDate && eventStart.getHours() === hour;
    });
  };

  // Calculate task block position and height spanning multiple hours if needed
  const getTaskBlockStyle = (event: CalendarEvent, hour: number) => {
    const eventStart = new Date(event.start);
    const eventEnd = new Date(event.end);
    const startMinutes = eventStart.getMinutes();
    const topPosition = (startMinutes / 60) * 100;
    const durationMinutes = (eventEnd.getTime() - eventStart.getTime()) / (1000 * 60);
    const heightPercentage = (durationMinutes / 60) * 100;
    return {
      top: `${topPosition}%`,
      height: `${heightPercentage}%`,
      position: 'absolute' as const,
      width: '90%',
      left: '5%',
      zIndex: 10
    };
  };

  return (
    <div className="calendar-planner">
      <div className="calendar-container">
        <div className="calendar-header">
          <h1 className="planner-title">Calendar Planner</h1>
          <div className="calendar-nav">
            <button className="nav-btn" onClick={goToPreviousWeek}>←</button>
            <button className="nav-btn" onClick={goToNextWeek}>→</button>
            <span className="month-year">{format(currentDate, 'MMMM yyyy')}</span>
          </div>
        </div>
        <div className="calendar-content">
          <div className="calendar-legend">
            {(() => {
              if (Object.values(weeklyHours).every(value => value === 0)) {
                return <span>No events found for this week.</span>;
              }
              return (
                <>
                  <div className="legend-item">
                    <div className="legend-color focus"></div>
                    <span>Focus {weeklyHours.focus.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color tasks"></div>
                    <span>Tasks {weeklyHours.tasks.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color target"></div>
                    <span>Focus target {weeklyHours.target.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color other"></div>
                    <span>Other work {weeklyHours.other.toFixed(1)}h</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color free"></div>
                    <span>Free {weeklyHours.free.toFixed(1)}h</span>
                  </div>
                </>
              );
            })()}
          </div>
          <div className="calendar-grid">
            <div className="time-header">GMT+3</div>
            {getWeekDays().map((day, index) => (
              <div 
                key={index} 
                className={`day-header ${isToday(day) ? 'today' : ''}`}
              >
                <div>{format(day, 'EEE d')}</div>
              </div>
            ))}
            {timeSlots.map(hour => (
              <React.Fragment key={hour}>
                <div className="time-slot">
                  {hour === 6 ? '6am' : hour === 12 ? '12pm' : hour === 23 ? '11pm' : hour > 12 ? `${hour-12}pm` : `${hour}am`}
                </div>
                {getWeekDays().map((day, dayIndex) => {
                  const eventsInSlot = getEventsForSlot(day, hour);
                  return (
                    <div key={`${hour}-${dayIndex}`} className="calendar-cell">
                      {eventsInSlot.map(event => (
                        <div
                          key={event.id}
                          className={`task-block ${event.type}`}
                          style={getTaskBlockStyle(event, hour)}
                          title={event.title}
                        >
                          <span>{event.title}</span>
                          <button 
                            className="delete-btn" 
                            style={{marginLeft: 8, fontSize: 10, background: '#dc3545', color: 'white', border: 'none', borderRadius: 3, cursor: 'pointer', padding: '0 6px'}} 
                            onClick={(e) => { e.stopPropagation(); handleDeleteEvent(event.id); }}
                            title="Удалить задачу"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
      <div className="task-sidebar">
        <div className="sidebar-header">
          <h2 className="sidebar-title">Create New Task</h2>
        </div>
        <div className="form-group">
          <input
            type="text"
            className="form-input"
            placeholder="Task name..."
            value={taskForm.title}
            onChange={(e) => setTaskForm({...taskForm, title: e.target.value})}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Duration</label>
          <div className="duration-controls">
            <button 
              className="duration-btn"
              onClick={() => setTaskForm({...taskForm, duration: Math.max(0.5, taskForm.duration - 0.5)})}
            >
              -
            </button>
            <input
              type="text"
              className="duration-input"
              value={`${taskForm.duration} hr`}
              readOnly
            />
            <button 
              className="duration-btn"
              onClick={() => setTaskForm({...taskForm, duration: taskForm.duration + 0.5})}
            >
              +
            </button>
          </div>
        </div>
        <div className="form-group">
          <label className="form-label">Task Type</label>
          <select 
            className="form-input"
            value={taskForm.type}
            onChange={(e) => setTaskForm({...taskForm, type: e.target.value as 'focus' | 'tasks' | 'target' | 'other'})}
          >
            <option value="focus">Focus</option>
            <option value="tasks">Tasks</option>
            <option value="target">Focus target</option>
            <option value="other">Other work</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea
            className="form-input"
            placeholder="Optional description..."
            value={taskForm.description}
            onChange={(e) => setTaskForm({...taskForm, description: e.target.value})}
            rows={3}
            style={{resize: 'vertical', minHeight: '60px'}}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Due date & time</label>
          <div className="datetime-inputs">
            <input
              type="date"
              className="schedule-input"
              value={taskForm.dueDate}
              onChange={(e) => setTaskForm({...taskForm, dueDate: e.target.value})}
            />
            <input
              type="time"
              className="schedule-input"
              value={taskForm.dueTime}
              onChange={(e) => setTaskForm({...taskForm, dueTime: e.target.value})}
            />
          </div>
          <div style={{fontSize: '12px', color: '#666', marginTop: '5px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span>📅 {format(new Date(taskForm.dueDate), 'EEEE, MMMM d, yyyy')} at {taskForm.dueTime}</span>
            <button 
              type="button"
              style={{fontSize: '10px', padding: '2px 6px', background: '#007bff', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer'}}
              onClick={() => setTaskForm({...taskForm, dueDate: format(new Date(), 'yyyy-MM-dd')})}
            >
              Today
            </button>
          </div>
        </div>
        <button 
          className="create-btn" 
          onClick={createTask}
          disabled={!taskForm.title.trim() || isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Task'}
        </button>
      </div>
    </div>
  );
};

export default Calendar;