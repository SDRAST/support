import logging

from support.arguments import initiate_option_parser

if __name__ == "__main__":
    # demonstrate minimum logging
    oldstyle = True

    import sys
    from support.logs import init_logging, get_loglevel, set_module_loggers
    
    examples = """Examples:
    program --help
      to get this output
    program --logfilepath /var/tmp
      useful when testing code without cluttering the log"""
    p = initiate_option_parser(__doc__, examples)
    # Add other options here
  
    
    # This cannot be delegated to another module or class
    if oldstyle:
      opts, args = p.parse_args(sys.argv[1:])
      
      mylogger = init_logging(logging.getLogger(),
                            loglevel         = get_loglevel(opts.file_loglevel),
                            consolevel       = get_loglevel(opts.console_loglevel),
                            logname          = opts.logpath+"/"+__name__+".log")
      loggers = set_module_loggers(eval(opts.modloglevels))   
    else:
      # this will also work
      args = p.parse_args()
  
      mylogger = init_logging(logging.getLogger(),
                            loglevel         = get_loglevel(args.file_loglevel),
                            consolevel       = get_loglevel(args.console_loglevel),
                            logname          = args.logpath+"/"+__name__+".log")
      loggers = set_module_loggers(eval(args.modloglevels))

  
