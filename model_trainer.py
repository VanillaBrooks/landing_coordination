from flight_path_det import PlanePath
import torch
import pprint, time, pymysql, os


class NeuralNetwork(torch.nn.Module):
    def __init__(self, D_in, Hidden_1, Hidden_2, Hidden_3, D_out):
        super(NeuralNetwork, self).__init__()

        self.LI = torch.nn.Linear(D_in, Hidden_1)
        self.L1 = torch.nn.Linear(Hidden_1, Hidden_2)
        self.L2 = torch.nn.Linear(Hidden_2, Hidden_2)
        self.L3 = torch.nn.Linear(Hidden_2, Hidden_2)
        self.L4 = torch.nn.Linear(Hidden_2, Hidden_2)
        self.L5 = torch.nn.Linear(Hidden_2, Hidden_2)
        self.L6 = torch.nn.Linear(Hidden_2, Hidden_2)
        self.L7 = torch.nn.Linear(Hidden_2, Hidden_3)
        self.LF = torch.nn.Linear(Hidden_3, D_out)


    def forward(self, x):
        initial = self.LI(x)

        L1 = self.L1(initial)
        L2 = self.L2(L1)
        L3 = self.L3(L2)
        L4 = self.L4(L3)
        L5 = self.L5(L4)
        L6 = self.L6(L5)
        L7 = self.L7(L6)

        pred = self.LF(L7)

        return pred

class DatabaseConnection():
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='brooks', password='pass', database='pubg4')
        self.cursor = self.conn.cursor()

    def op(self, query, arg_tuple=()):
        self.cursor.execute(query, arg_tuple)
        raw_data = self.cursor.fetchall()

        data = [row[:-1] for row in raw_data]
        print('the length of the sql data is ', len(data))
        return data
def percentdec(prev, new):
    x =  100* ((prev- new) / prev)
    x = float(str(x)[:5])
    return x

def probabilities(train, expect):
    ph = []
    index = 0

    data = list(zip(train,expect))
    d2 = data[:]
    removed = 0

    for pair in d2:
        row = pair[1]
        sum = 0
        nested_ph = []
        for item in row:
            sum += item

        # print('sum is %s for %s index is %s' % (sum, row, index))
        if sum <= 30 or sum > 100:
            # print('sum is %s for %s index is %s' % (sum, row, index))
            data.pop(index)
            removed += 1
            continue

        for item in row:
            nested_ph.append(item/sum)
        ph.append(nested_ph)
        index += 1

    if removed:
        print('there were %s values removed'%(removed))
        for pair in data:
            row = pair[1]
            sum = 0
            for item in row:
                sum += item
            if sum <= 30 or sum > 100:
                print('fuck dude you didnt get rid of the index for the sum', sum)
    nt, ne = list(zip(*data))

    return nt,ph


D_in = 25
Hidden_1 = 50
Hidden_2 = 40
Hidden_3 = 30
D_out = 25
epochs = 5000000
path = r'D:\Python\pytorch\model_2_3'

if __name__ == '__main__':
    torch.set_printoptions(threshold=10000)
    db = DatabaseConnection()

    training_data, expected_results = probabilities(db.op('SELECT * from distances'), db.op('SELECT * from dropcount'))
    print('len training data %s len expected results %s' % (len(training_data), len(expected_results)))
    # training_data = training_data[:400]
    # expected_results = expected_results[:400]

    N = len(training_data)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = NeuralNetwork(D_in, Hidden_1, Hidden_2, Hidden_3, D_out)
    model.to(device)

    if os.path.exists(path):
        print('loaded previous model')
        model.load_state_dict(torch.load(path))



    training_data = torch.Tensor(training_data).to(device)
    expected_results = torch.Tensor(expected_results).to(device)
    criterion = torch.nn.SmoothL1Loss(size_average=False, reduce=True)

    optimizer = torch.optim.RMSprop(model.parameters(), lr=1e-5)


    prev = 1
    # time.sleep(363632)
    for t in range(epochs):
        predicted = model(training_data).view(N,D_out)

        percent = str((100* t) / epochs)[:6]
        loss = criterion(predicted, expected_results)
        if t % 5000 == 0:
            print('iter: %s percent done: %s loss: %s loss decrease: %s' % (t,percent, loss.item(), percentdec(prev, float(loss.item()))))
            prev = float(loss.item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (t%10000) == 0:
            torch.save(model.state_dict(), path)

    torch.save(model.state_dict(), path)

