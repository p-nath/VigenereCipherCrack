from operator import itemgetter
import argparse

# assumption - 2 < keyword length < 20
freq = {
    'A': .082, 'B': .015, 'C': .028, 'D': .043,
    'E': .127, 'F': .022, 'G': .020, 'H': .061,
    'I': .070, 'J': .002, 'K': .008, 'L': .040,
    'M': .024, 'N': .067, 'O': .075, 'P': .019,
    'Q': .001, 'R': .060, 'S': .063, 'T': .091,
    'U': .028, 'V': .010, 'W': .023, 'X': .001,
    'Y': .020, 'Z': .001
}

def GetFactorsLessThan20(x):
  factors = []
  for i in xrange(3, 20):
    if x % i == 0:
      factors.append(i)
  return factors

def KasikiAnalysis(data, subseqlen):
  l =[]
  for i in xrange(len(data) - subseqlen):
    m = data.find(data[i:i + subseqlen], i + subseqlen) 
    if m != -1:
      l.append(m - i)

  keylens = [0 for i in xrange(20)]
  for i in l:
    factors = GetFactorsLessThan20(i)
    for j in factors:
      keylens[j] += 1
  return keylens

def PredictKeyLength(data):
  keylens3 = KasikiAnalysis(data, 3)
  keylens4 = KasikiAnalysis(data, 4)

  keylens = []
  for i in xrange(3,20):
    keylens.append((i, keylens4[i]+keylens3[i]))
  keylens = sorted(keylens, key=itemgetter(1), reverse = True)
  return keylens


def crack(data, keylength, index, key_chi):
  letterfreq = [0 for i in xrange(26)]
  totchars = 0
  l = {}
  for i in xrange(index, len(data), keylength):
    letterfreq[ord(data[i]) - ord('A')] += 1
    totchars += 1
  avg_char_freq = [(i*1.0)/totchars for i in letterfreq]
 # key prediction using chi-squared statistic used to compare the freq distributions
 # ref - http://practicalcryptography.com/cryptanalysis/text-characterisation/chi-squared-statistic/
  for i in xrange(26):
    l[chr(ord('A') + i)] = 0
    for j in xrange(26):
      x = round(((letterfreq[(i + j) % 26 ] - freq[chr(65 + j)] * totchars) ** 2) / (freq[chr(j + 65)] * totchars), 3)
      l[chr(ord('A') + i)] += x
  key_chi.append(min(l, key=l.get))

def PredictKeys(data):
  keylens = PredictKeyLength(data)
  keys = []
  print "The probabale key-lengths and their frequencies(top 5 with most frequencies) are: "
  print "Length \t Frequencies"
  for i in xrange(5):
    print '{:>6}'.format(keylens[i][0]),"\t",'{:>11}'.format(keylens[i][1])
  #print keylens
  # i chose to test the keyword lengths of 5 and 10 since repetitions for them were the highest
  for i in xrange(5):
    key_chi = []
    for j in xrange(keylens[i][0]):
      crack(data, keylens[i][0], j, key_chi)
    keys.append(''.join(key_chi))
  return keys

def decipher(data, key, decrypted_text, index, key_len):
  for i in xrange(key_len):
    if (index + i) >= len(data):
      return
    x = 26 + (ord(data[index + i]) - ord(key[i]) + 65)
    if x > 90:
      x = x%90 + 64
    decrypted_text.append(chr(x))


def main():
  args = ParseArgs()
  fin = args.fin
  fout = args.fout
  decipher_key = args.key

  with open(fin, 'r') as myfile:
    data = myfile.read().replace('\n', '')


  if args.k == True:
    keys = PredictKeys(data)
    print "The predicted keys are: "
    for i in xrange(len(keys)):
      print str(i+1) + ". " + keys[i]
    print "Choose one of the keys to decrypt cipher text(choose number): " 
    x = int(raw_input())
    decipher_key = keys[x-1]

  decrypted_text = []
  for i in xrange(0, len(data), len(decipher_key)):
    decipher(data, decipher_key, decrypted_text, i, len(decipher_key))
      
  if fout == -1:
    print ''.join(decrypted_text)
  else:
    f = open(fout, 'w')
    f.write(''.join(decrypted_text))
  print "The decrypted cipher text has been written in", fout

def ParseArgs():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', action="store", dest="fin", default=-1,
                     help='Specify filename of encrypted cipher text')
  parser.add_argument('-o', action="store", dest="fout", default=-1,
                     help='Specify output file to store decrypted plain text')
  parser.add_argument('-k', action="store_true", default=False)
  parser.add_argument('-d', action="store", dest="key", type=str)
  return parser.parse_args()

if __name__ == '__main__':
  main()


