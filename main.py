from __future__ import print_function
import sys
import os
import codecs

import code
import code.config_parser as config_parser
import code.generator as generator
import code.parser as parser
import code.tester as tester
import code.codec as codec

                    
def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
    import sys
    args = sys.argv
    
    show_trigger = False
    encoding = 'UTF-8'
    operation = None
    config_file = os.path.join('resources', 'default.ini')
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-h' or arg == '--help':
            print('Circle code generator')
            print('  -c, --config       path : Set config file')
            print('  -e, --encoding     name : Encoding for files.', encoding, 'by default')
            print('  -g, --gen-inline    msg : Generate image from message specified')
            print('  -G, --gen-file     path : Generate image from file specified')
            print('  -h, --help              : Help')
            print('  -p, --parse        path : Parse code from image')
            print('  -P, --force-parse  path : Parse code from distorted image')
            print('  -t, --test              : Run tests')
            print('  -T, --test-draw         : Draw test image')
            print('  -s, --show              : Show generated result on screen')
            exit()
        
        if arg == '-c' or arg == '--config':
            if i + 1 < len(args):
                i += 1
                config_file = args[i]
            else:
                print_err('Not enough arguments: path to config is not specified. Using default.')
                
        if arg == '-g' or arg == '--gen-inline':
            if i + 1 < len(args):
                operation = ('gen-inline', args[i+1])
                i += 1
            else:
                print_err('Not enough arguments: message is not specified. Aborting.')
                exit()
        
        if arg == '-G' or arg == '--gen-file':
            if i + 1 < len(args):
                operation = ('gen-file', args[i+1])
                i += 1
            else:
                print_err('Not enough arguments: file not specified. Aborting.')
                exit()
    
        if arg == '-e' or arg == '--encoding':
            if i + 1 < len(args):
                i += 1
                encoding = args[i]
            else:
                print_err('Not enough arguments: encoding is not specified. Using default.')
            
        if arg == '-p' or arg == '--parse':
            if i + 1 < len(args):
                operation = ('parse', args[i+1])
                i += 1
            else:
                print_err('Not enough arguments: message is not specified. Aborting.')
                exit()
        
        if arg == '-P' or arg == '--force-parse':
            if i + 1 < len(args):
                operation = ('Fparse', args[i+1])
                i += 1
            else:
                print_err('Not enough arguments: message is not specified. Aborting.')
                exit()
                
        if arg == '-t' or arg == '--test':
            print('Running tests')
            tester.test('tests', code)
            print('Completed.')
            exit()
        
        if arg == '-T' or arg == '--test-draw':
            config = config_parser.Config(config_file, encoding)
            gen = generator.Generator(config)
            gen.generate(None)
            exit()
        
        if arg == '-s' or arg == '--show':
            show_trigger = True
        
        i += 1
    
    if operation == None:
        print_err('No operation specified. Please, use flags -g, -G or -p')
        exit()
    
    config = config_parser.Config(config_file, encoding)
    coder = codec.Codec(config)
    
    if operation[0] == 'gen-inline':
        msg = operation[1]
        msg = coder.encode(msg)

        gen = generator.Generator(config)
        gen.generate(msg)
        
        if show_trigger:
            gen.show()

    elif operation[0] == 'gen-file':
        f = codecs.open(operation[1], 'r', encoding)
        msg = f.read()
        msg = coder.encode(msg)

        gen = generator.Generator(config)
        gen.generate(msg)
        
        if show_trigger:
            gen.show()

    elif operation[0] == 'parse':
        prs = parser.Parser(config)
        msg = prs.parse(operation[1])
        print(coder.decode(msg))
    
    elif operation[0] == 'Fparse':
        prs = parser.Parser(config)
        msg = prs.force_parse(operation[1])
        print(coder.decode(msg))
        
        