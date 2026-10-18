-- A report contact stays separate from the public item projection.
ALTER TABLE items ADD COLUMN contact_email TEXT CHECK (
    contact_email IS NULL OR
    (length(contact_email) BETWEEN 5 AND 120 AND
     contact_email LIKE '%_@_%._%' AND instr(contact_email, ' ') = 0)
);
