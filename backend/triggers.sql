-- 🔹 TRIGGERS FOR TASKS TABLE

DELIMITER $$

-- 1️⃣ After INSERT on tasks
CREATE TRIGGER trg_task_insert
AFTER INSERT ON tasks
FOR EACH ROW
BEGIN
    UPDATE daily_plan
    SET total_task = total_task + 1,
        completed_task = completed_task + IF(NEW.status = 'Completed', 1, 0)
    WHERE plan_id = NEW.plan_id;
END$$


-- 2️⃣ After UPDATE on tasks
CREATE TRIGGER trg_task_update
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    -- Adjust completed_task count if status changed
    IF OLD.status <> NEW.status THEN
        UPDATE daily_plan
        SET completed_task = completed_task 
            + (CASE 
                   WHEN NEW.status = 'Completed' AND OLD.status = 'Incomplete' THEN 1
                   WHEN NEW.status = 'Incomplete' AND OLD.status = 'Completed' THEN -1
                   ELSE 0
               END)
        WHERE plan_id = NEW.plan_id;
    END IF;
END$$


-- 3️⃣ After DELETE on tasks
CREATE TRIGGER trg_task_delete
AFTER DELETE ON tasks
FOR EACH ROW
BEGIN
    UPDATE daily_plan
    SET total_task = total_task - 1,
        completed_task = completed_task - IF(OLD.status = 'Completed', 1, 0)
    WHERE plan_id = OLD.plan_id;
END$$

DELIMITER ;
