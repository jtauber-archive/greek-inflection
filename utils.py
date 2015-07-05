class Counter:
    def __init__(self):
        self.success_count = 0
        self.skip_count = 0
        self.fail_count = 0
        self.first_fail = None
        self.first_skip = None

    def success(self):
        self.success_count += 1

    def skip(self, message):
        self.skip_count += 1
        if self.first_skip is None:
            self.first_skip = message

    def fail(self, message):
        self.fail_count += 1
        if self.first_fail is None:
            self.first_fail = message

    def results(self):
        print("{} success; {} fail; {} skipped".format(self.success_count, self.fail_count, self.skip_count))
        if self.first_fail:
            print("first fail: {}".format(self.first_fail))
        if self.first_skip:
            print("first skip: {}".format(self.first_skip))
