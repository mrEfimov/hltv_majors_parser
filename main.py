from parser.parser import get_majors, get_majors_stats


def main():
    get_majors()

    get_majors_stats('player')
    get_majors_stats('team')


if __name__ == '__main__':
    main()
