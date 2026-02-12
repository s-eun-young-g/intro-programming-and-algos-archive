(begin
  ; (map f lst) applies function f to each element of lst and returns a new list of results
  (define (map f lst)
    (if (list? lst)
        (if (equal? lst ())
            ()
            (cons (f (car lst)) (map f (cdr lst))))
        ; raise error
        (error)))

  ; (filter f lst) returns a list of all elements in lst for which (f element) is true
  (define (filter f lst)
    (if (list? lst)
        (if (equal? lst ())
            ()
            (let ((rest (filter f (cdr lst))))
              (if (f (car lst))
                  (cons (car lst) rest)
                  rest)))
        ; raise error
        (error)))

  ; (reduce f lst init) reduces the list lst by applying f cumulatively, starting from init.
  (define (reduce f lst init)
    (if (list? lst)
        (if (equal? lst ())
            init
            (reduce f (cdr lst) (f init (car lst))))
        ; raise error
        (error))))
